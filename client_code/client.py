"""
Client-side Firebase integration for Anvil (Firebase Web SDK v8).

Provides:
- Models: FirebaseConfig, ActionMap for configuration and action routing.
- FirebaseClient: wraps Firebase init, messaging, SW registration, and topic/actions.
"""

import re

import anvil.js
import anvil.server
from anvil import *  # noqa: F403
from anvil import Notification

from .client_utils import DEFAULT_SERVICE_WORKER, in_debug
from .validators import Validators


# MARK: Models & configuration

class FirebaseConfig:
    def __init__(
        self,
        api_key: str,
        auth_domain: str,
        project_id: str,
        storage_bucket: str,
        messaging_sender_id: str,
        app_id: str,
        measurement_id: str,
    ):
        """
        Initializes a new instance of the FirebaseConfig class.

        Args:
            api_key (str): The API key for your Firebase project.
            auth_domain (str): The domain for your Firebase authentication.
            project_id (str): The ID for your Firebase project.
            storage_bucket (str): The name of your Firebase storage bucket.
            messaging_sender_id (str): The sender ID for Firebase messaging.
            app_id (str): The ID for your Firebase app.
            measurement_id (str): The ID for Firebase analytics.
        """
        validator = Validators()
        self.api_key = validator.validate_string(api_key, "api_key")
        self.auth_domain = validator.validate_string(auth_domain, "auth_domain")
        self.project_id = validator.validate_string(project_id, "project_id")
        self.storage_bucket = validator.validate_string(
            storage_bucket, "storage_bucket"
        )
        self.messaging_sender_id = validator.validate_string(
            messaging_sender_id, "messaging_sender_id"
        )
        self.app_id = validator.validate_string(app_id, "app_id")
        self.measurement_id = validator.validate_string(
            measurement_id, "measurement_id"
        )

    def to_dict(self) -> dict:
        """Return Firebase config as a dict in Firebase JS expected casing."""
        return {
            "apiKey": self.api_key,
            "authDomain": self.auth_domain,
            "projectId": self.project_id,
            "storageBucket": self.storage_bucket,
            "messagingSenderId": self.messaging_sender_id,
            "appId": self.app_id,
            "measurementId": self.measurement_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FirebaseConfig":
        """Create a FirebaseConfig from a JS-style dict."""
        return cls(
            api_key=d["apiKey"],
            auth_domain=d["authDomain"],
            project_id=d["projectId"],
            storage_bucket=d["storageBucket"],
            messaging_sender_id=d["messagingSenderId"],
            app_id=d["appId"],
            measurement_id=d["measurementId"],
        )


class ActionMap:
    def __init__(
        self,
        action_name: str,
        endpoint: str = None,
        full_url: str = None,
        params: dict = None,
        data: dict = None,
        auth_key: str = None,
        is_api_endpoint: bool = False,
    ):
        """
        Represents a mapping from an action name to an endpoint or URL.

        Attributes:
            action_name (str): The name of the action.
            endpoint (str): The endpoint for the action.
            full_url (str): The full URL for the action.
            params (dict): The parameters to be included in the URL when the action's URL is not an API endpoint.
            data (dict): The data to be included in the body of the POST request when the action's URL is an API endpoint.
            auth_key (str): The Bearer token to be included in the 'Authorization' header of the POST request when the action's URL is an API endpoint. The header will be formatted as 'Authorization: Bearer {auth_key}'.
            is_api_endpoint (bool): Whether the action's URL is an API endpoint.
        """
        if not isinstance(endpoint, str) and not isinstance(full_url, str):
            raise TypeError("endpoint or full_url must be strings.")

        validator = Validators()

        self.action_name = validator.validate_string(action_name, "action_name")
        self.endpoint = validator.validate_string(endpoint, "endpoint", True)
        self.full_url = validator.validate_url(full_url, "full_url", True)
        self.params = validator.validate_dict(params, "params", optional=True) or {}
        self.data = validator.validate_dict(data, "data", optional=True) or {}
        self.auth_key = validator.validate_string(auth_key, "auth_key", True)
        self.is_api_endpoint = (
            validator.validate_bool(is_api_endpoint, "is_api_endpoint", True) or False
        )

    @property
    def full_url(self):
        return self._full_url if self._full_url else self._build_url_from_endpoint()

    @full_url.setter
    def full_url(self, value):
        self._full_url = value

    def __str__(self):
        return f"ActionMap(action_name={self.action_name})"

    def __repr__(self):
        return f"<{str(self)}>"

    def _build_url_from_endpoint(self):
        if not isinstance(self.endpoint, str):
            raise TypeError("endpoint must be a string.")

        # Check if the endpoint is already a full URL
        if self.endpoint.startswith("http://") or self.endpoint.startswith("https://"):
            return self.endpoint

        # If not, proceed to build the full URL
        endpoint = re.sub(r"^/", "", self.endpoint)  # strip "/" from the beginning

        if self.is_api_endpoint:
            base_url = anvil.server.get_api_origin()
        elif in_debug():
            base_url = anvil.server.get_app_origin()
        else:
            base_url = anvil.server.get_app_origin("published")

        return f"{base_url}/{endpoint}"


# MARK: Firebase client

class FirebaseClient:
    """Client wrapper around Firebase Web SDK (v8) for the Anvil client runtime."""
    def __init__(
        self,
        config: FirebaseConfig,
        public_vapid_key: str = None,
        service_worker_url: str = DEFAULT_SERVICE_WORKER,
        message_handler: callable = None,
        save_token_handler: callable = None,
        subscribe_handler: callable = None,
        unsubscribe_handler: callable = None,
        allow_notification_str: str = "Please allow notification!",
        topics: list = None,
        action_maps: list = None,
        with_logging: bool = False,
    ):
        """
        Initializes a new instance of the FirebaseClient class.

        Args:
            config (FirebaseConfig): The Firebase project configuration.
            service_worker_url (str, optional): The URL to your custom service worker.
            public_vapid_key (str, optional): The public VAPID key for web push. Defaults to None.
            message_handler (callable, optional): A function to handle incoming messages. Defaults to None.
            save_token_handler (callable, optional): A function to handle saving of device token. Defaults to None.
            subscribe_handler (callable, optional): A function to handle topic subscription. Defaults to None.
            unsubscribe_handler (callable, optional): A function to handle topic unsubscription. Defaults to None.
            topics (list, optional): A list of topics to subscribe to. Defaults to None.
            allow_notification_str (str, optional): The message to display when the user has not allowed notifications. Defaults to "Please allow notification!".
            with_logging (bool, optional): Whether to print log messages. Defaults to False.
        """
        validator = Validators()
        self._messaging = None
        self.token = None
        self.registration = None

        self.config = validator.validate_specific_class(
            config, "config", FirebaseConfig
        )
        self.public_vapid_key = validator.validate_string(
            public_vapid_key, "public_vapid_key", True
        )
        self.service_worker_url = validator.validate_string(
            service_worker_url, "service_worker_url", True
        )
        self.message_handler = validator.validate_callable(
            message_handler, "message_handler", True
        )
        self.save_token_handler = validator.validate_callable(
            save_token_handler, "save_token_handler", True
        )
        self.subscribe_handler = validator.validate_callable(
            subscribe_handler, "subscribe_handler", True
        )
        self.unsubscribe_handler = validator.validate_callable(
            unsubscribe_handler, "unsubscribe_handler", True
        )
        self.topics = validator.validate_list_of_strings(topics, "topics", True)
        self.allow_notification_str = validator.validate_string(
            allow_notification_str, "allow_notification_str", True
        )
        self.action_maps = validator.validate_list_of_specific_class(
            action_maps, "action_maps", ActionMap, True
        )
        self.with_logging = (
            validator.validate_bool(with_logging, "with_logging", True) or False
        )

        self.id = id(self)

    # MARK: - Magic methods

    def __str__(self):
        return f"FirebaseClient(id={self.id})"

    def __repr__(self):
        return f"<{str(self)}>"

    # MARK: - Public methods

    def initialize_app(self) -> None:
        """Initialize Firebase app/messaging, handlers, and service worker.

        Steps:
        - firebase.initializeApp(config)
        - firebase.messaging() and store reference
        - Register message/token handlers
        - Register service worker and wire it to messaging

        Returns:
            False on failure (exception handled internally); otherwise None.
        """
        try:
            anvil.js.window.firebase.initializeApp(self.config.to_dict())
            self._log("Firebase app initialized.")

            self._messaging = anvil.js.window.firebase.messaging()
            self._log("Firebase messaging service initialized.")

            self._setup_message_handler()
            self._setup_token_refresh_handler()
            self._register_service_worker()
        except Exception as e:
            self._handle_error("initializing app", e)
            return False

    def request_notification_permission(self) -> bool:
        """
        Requests the user's permission to send notifications.

        This method uses the Notification API to ask the user's permission for showing notifications.
        If the permission is granted, it returns True, otherwise False.
        If an error occurs during the process, it is handled by the `_handle_error` method and False is returned.

        Returns:
            bool: True if permission is granted, False otherwise.
        """
        try:
            self._log("Requesting notification permission.")
            permission = anvil.js.await_promise(
                anvil.js.window.Notification.requestPermission()
            )
            self._log(f"Permission status: {permission}")
            self._handle_permission(permission)
            response = True if permission == "granted" else False
        except Exception as e:
            self._handle_error("requesting notification permission", e)
            response = False

        return response

    def subscribe_to_topic(self, topic: str) -> None:
        """
        Subscribes the device to a specified topic.

        This method takes a topic name as an argument and subscribes the device to this topic.
        If a subscribe handler is set, it calls the handler with the topic name and the device token.
        If no subscribe handler is set, it logs an error message using the `_handle_error` method indicating that no subscribe handler is set.

        The method logs the successful subscription to a topic using the `_log` method, and any errors that occur during the process are logged and handled by the `_handle_error` method.

        Args:
            topic (str): The name of the topic to subscribe to.

        Returns:
            None
        """
        if self.subscribe_handler:
            try:
                self.subscribe_handler(topic, self.token)
                self._log(f"Subscribed to topic: {topic}")
            except Exception as e:
                self._handle_error("Subscribing to topic", e)
        else:
            self._handle_error("Subscribing to topic", "No subscribe handler set.")

    def unsubscribe_from_topic(self, topic: str) -> None:
        """
        Unsubscribes the device from a specified topic.

        This method takes a topic name as an argument and unsubscribes the device from this topic.
        If an unsubscribe handler is set, it calls the handler with the topic name and the device token.
        If no unsubscribe handler is set, it logs an error message using the `_handle_error` method indicating that no unsubscribe handler is set.

        The method logs the successful unsubscription from a topic using the `_log` method, and any errors that occur during the process are logged and handled by the `_handle_error` method.

        Args:
            topic (str): The name of the topic to unsubscribe from.

        Returns:
            None
        """
        if self.unsubscribe_handler:
            try:
                self.unsubscribe_handler(topic, self.token)
                self._log(f"Unsubscribed from topic: {topic}")
            except Exception as e:
                self._handle_error("Unsubscribing from topic", e)
        else:
            self._handle_error(
                "Unsubscribing from topic", "No unsubscribe handler set."
            )

    def add_action_map(self, action_map: ActionMap) -> bool:
        """
        Adds an action map to the service worker.

        This function takes an ActionMap object as an argument.
        It sends a message to the active service worker with the type 'ADD_ACTION_MAP' and the details of the action map.
        The details include the action name, the full URL for the action, and the token for the action.

        If the 'with_logging' attribute of the class is True, it logs a message indicating that the action map was sent to the service worker.

        If an error occurs while sending the message, it logs the error and calls the '_handle_error' method with a message indicating the error and the exception.

        Args:
            action_map (ActionMap): The action map to add.

        Returns:
            bool: True if the action map was successfully added, False otherwise.
        """
        try:
            sw = (
                self.registration.active
                or self.registration.waiting
                or self.registration.installing
            )
            sw.postMessage(
                {
                    "type": "ADD_ACTION_MAP",
                    "actionName": action_map.action_name,
                    "fullUrl": action_map.full_url,
                    "params": action_map.params,
                    "data": action_map.data,
                    "authKey": action_map.auth_key,
                }
            )
            self._log(
                f"Sent action map for {action_map.action_name} to service worker."
            )
            return True
        except Exception as e:
            self._handle_error(
                f"Error adding action map for {action_map.action_name} to service worker",
                e,
            )
            return False

    # MARK: - Private methods

    def _add_action_maps_to_service_worker(self):
        """Send all configured ActionMaps to the current service worker."""
        if not self.registration:
            return

        for action_map in self.action_maps:
            self.add_action_map(action_map)
            self._log(f"Added action map for {action_map.action_name}.")

    def _handle_permission(
        self, permission, notification_str: str = None, timeout: int = 0
    ) -> None:
        """Handle permission result string and optionally show a prompt."""
        if notification_str is None:
            notification_str = self.allow_notification_str

        if permission == "denied":
            try:
                Notification(notification_str, timeout=timeout).show()
            except Exception as e:
                self._handle_error("showing notification", e)
            self._log("Notification permission denied.")
        elif permission == "granted":
            self._add_action_maps_to_service_worker()
            self._log("Notification permission granted.")
        else:
            self._log("Notification permission not set.")

    def _log(self, message):
        """Print a log line when with_logging is enabled."""
        if self.with_logging:
            print(f"FirebaseClient Log: {message}")

    def _on_message(self, payload):
        """Convert payload to a Python dict and dispatch to message_handler if set."""
        payload_dict = self._convert_payload_to_dict(payload)
        self._log(f"Message received: {payload_dict}")

        if self.message_handler:
            try:
                self.message_handler(payload_dict)
            except Exception as e:
                self._handle_error("handling message", e)
        else:
            self._log("No message handler set.")

    def _register_service_worker(self):
        """Register the service worker, send config, and prime token/topics."""
        try:
            self.registration = anvil.js.await_promise(
                anvil.js.window.navigator.serviceWorker.register(
                    self.service_worker_url
                )
            )

            self._log("Service worker registered.")

            self._set_service_worker()
            self._update_service_worker_firebase_config()

            self._retrieve_and_save_device_token()
            self._subscribe_to_topics()
        except Exception as e:
            self._handle_error("registering service worker", e)

    def _retrieve_and_save_device_token(self):
        """Get current FCM token (optionally using VAPID key) and call save handler."""
        token_options = (
            {"vapidKey": self.public_vapid_key} if self.public_vapid_key else {}
        )

        try:
            token = anvil.js.await_promise(self._messaging.getToken(token_options))
            self.token = token or None

            if self.token and self.save_token_handler:
                self.save_token_handler(self.token)
                self._log("Device token saved.")
            else:
                self._log("Device token not saved.")
        except Exception as e:
            self._handle_error("retrieving device token", e)

    def _set_service_worker(self):
        """Bind the Messaging instance to the registered service worker."""
        if not self.registration:
            return

        self._messaging.useServiceWorker(self.registration)
        self._log("Service worker set.")

    def _setup_message_handler(self):
        """Subscribe to foreground messages and route them to _on_message."""
        self._messaging.onMessage(self._on_message)
        self._log("Message handler set.")

    def _setup_token_refresh_handler(self):
        """Register token refresh callback to persist new tokens."""
        self._messaging.onTokenRefresh(self._retrieve_and_save_device_token)
        self._log("Token refresh handler set.")

    def _subscribe_to_topics(self):
        """Subscribe to all configured topics using the provided handler."""
        if not self.subscribe_handler:
            self._log("No subscribe handler set.")
            return

        for topic in (self.topics or []):
            self.subscribe_to_topic(topic)

    def _update_service_worker_firebase_config(self):
        """Post the Firebase config to the active/waiting/installing service worker."""
        if not self.registration:
            return

        try:
            sw = (
                self.registration.active
                or self.registration.waiting
                or self.registration.installing
            )
            sw.postMessage(
                {"type": "SET_FIREBASE_CONFIG", "firebaseConfig": self.config.to_dict()}
            )
            self._log("Firebase config sent to service worker.")
        except Exception as e:
            self._handle_error("updating service worker firebase config", e)

    @staticmethod
    def _convert_payload_to_dict(payload):
        """Best-effort conversion of JS proxy payloads to native Python types."""
        def is_proxy(obj):
            return "proxy" in str(type(obj)).lower()

        def convert_proxy_object(payload_obj):
            if is_proxy(payload_obj):
                # Convert proxylist to Python list
                try:
                    return [convert_proxy_object(item) for item in payload_obj]
                except Exception:
                    # Convert proxy object to Python dictionary
                    try:
                        return {
                            key: convert_proxy_object(value)
                            for key, value in dict(payload_obj).items()
                        }
                    except Exception as e:
                        # Handle exceptions, optionally log them
                        print(f"Error converting payload: {e}")
                        return payload_obj
            else:
                return payload_obj

        return convert_proxy_object(payload)

    @staticmethod
    def _handle_error(action, error):
        """Print a standardized error line.

        Args:
            action: Description of the operation that failed.
            error: Exception or string with error information.
        """
        print(f"Error {action}: {error}")
