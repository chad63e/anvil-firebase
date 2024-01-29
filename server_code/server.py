from typing import Optional, Union

import anvil.media
import anvil.secrets
import anvil.server
import firebase_admin
from firebase_admin import credentials, initialize_app, messaging

from .messages import (
    BatchResponse,
    Message,
    MulticastMessage,
    Response,
    SimpleMessage,
    TopicManagementResponse,
    WebpushConfig,
    WebpushFCMOptions,
    WebpushNotification,
    WebpushNotificationAction,
)
from .server_utils import FCMServiceAccountCredentials


class FirebaseServer:
    def __init__(self, with_logging: Optional[bool] = True):
        self.with_logging = with_logging

    # --- PUBLIC METHODS ---

    def initialize_firebase_admin(
        self, service_account_creds: FCMServiceAccountCredentials
    ) -> bool:
        """
        Initializes the Firebase Admin SDK with the provided service account credentials.

        Parameters:
        - service_account_creds (FCMServiceAccountCredentials): The FCM service account credentials.

        Returns:
        bool: True if the Firebase Admin SDK was successfully initialized, False otherwise.
        """
        creds_path = service_account_creds.get_temp_file_path()
        cred = credentials.Certificate(creds_path)
        if not firebase_admin._apps:
            initialize_app(cred)
        return bool(firebase_admin._apps)

    def subscribe_to_topic(
        self,
        topic: str,
        token: str,
    ) -> TopicManagementResponse:
        """
        Subscribes a device to a topic.

        Parameters:
        - topic (str): The topic to subscribe to.
        - token (str): The FCM device token of the device.

        Returns:
        messaging.TopicManagementResponse: The response from the FCM server.
        """
        fcm_response = messaging.subscribe_to_topic(token, topic)
        response = TopicManagementResponse.from_fcm_response(fcm_response)

        self._log(
            f"Subscribed {response.success_count} tokens to topic {topic} successfully"
        )

        return response

    def unsubscribe_from_topic(
        self,
        topic: str,
        token: str,
    ) -> TopicManagementResponse:
        """
        Unsubscribes a device from a topic.

        Parameters:
        - topic (str): The topic to unsubscribe from.
        - token (str): The FCM device token of the device.

        Returns:
        messaging.TopicManagementResponse: The response from the FCM server.
        """
        fcm_response = messaging.unsubscribe_from_topic(token, topic)
        response = TopicManagementResponse.from_fcm_response(fcm_response)

        self._log(
            f"Unsubscribed {response.success_count} tokens from topic {topic} successfully"
        )

        return response

    def send(
        self,
        message: Union[Message, SimpleMessage],
        dry_run: Optional[bool] = False,
    ) -> Response:
        """
        Sends a message to the FCM server.

        Parameters:
        - message (Union[Message, MulticastMessage, SimpleMessage]): The message to send.
        - dry_run (bool): Whether to send the message in the dry run mode.

        Returns:
        messaging.BatchResponse: The response from the FCM server.
        """

        if not isinstance(message, (Message, SimpleMessage)):
            raise TypeError(
                "The message must be an instance of Message or SimpleMessage."
            )

        message = self._compile_message(message)

        try:
            fcm_response = messaging.send(message, dry_run=dry_run)
            response = Response.from_fcm_response(fcm_response)
        except Exception as e:
            response = Response.from_fcm_response(e)

        self._log(f"Message Response: {response}")

        return response

    def send_all(
        self,
        messages: list[Union[Message, SimpleMessage]],
        dry_run: Optional[bool] = False,
    ) -> BatchResponse:
        """
        Sends a list of messages to the FCM server.

        Parameters:
        - messages (list[Union[Message, SimpleMessage]]): The messages to send.
        - dry_run (bool): Whether to send the messages in the dry run mode.

        Returns:
        messaging.BatchResponse: The response from the FCM server.
        """

        if not all(
            isinstance(message, (Message, SimpleMessage)) for message in messages
        ):
            raise TypeError(
                "The messages must be instances of Message or SimpleMessage."
            )

        messages = [self._compile_message(message) for message in messages]

        fcm_response = messaging.send_all(messages, dry_run=dry_run)
        response = BatchResponse.from_fcm_response(fcm_response)

        self._log(f"Message Response: {response}")

        return response

    def send_multicast(
        self,
        message: MulticastMessage,
        dry_run: Optional[bool] = False,
    ) -> BatchResponse:
        """
        Sends a multicast message to the FCM server.

        Parameters:
        - message (MulticastMessage): The message to send.
        - dry_run (bool): Whether to send the message in the dry run mode.

        Returns:
        messaging.BatchResponse: The response from the FCM server.
        """

        if not isinstance(message, MulticastMessage):
            raise TypeError("The message must be an instance of MulticastMessage.")

        message = self._compile_multicast_message(message)

        fcm_response = messaging.send_multicast(message, dry_run=dry_run)
        response = BatchResponse.from_fcm_response(fcm_response)

        self._log(f"Message Response: {response}")

        return response

    # --- PRIVATE METHODS ---

    def _compile_webpush_notification_actions(self, message_dict: dict):
        actions = message_dict.get("actions") or []
        fcm_actions = []
        for action in actions:
            if isinstance(action, WebpushNotificationAction):
                fcm_action = messaging.WebpushNotificationAction(**action.to_dict())
                fcm_actions.append(fcm_action)

        if fcm_actions:
            return fcm_actions
        else:
            return None

    def _compile_webpush_notification(self, message_dict: dict):
        notification = message_dict.get("notification")
        if isinstance(notification, WebpushNotification):
            notification = notification.to_dict()

        if notification:
            notification["actions"] = self._compile_webpush_notification_actions(
                notification
            )
            return messaging.WebpushNotification(**notification)
        else:
            return None

    def _compile_webpush_config(self, message_dict: dict):
        webpush = message_dict.get("webpush")

        if isinstance(webpush, WebpushConfig):
            webpush = webpush.to_dict()

        if webpush:
            webpush["notification"] = self._compile_webpush_notification(webpush)

            return messaging.WebpushConfig(**webpush)
        else:
            return None

    def _compile_fcm_options(self, message_dict: dict):
        fcm_options = message_dict.get("fcm_options")
        if isinstance(fcm_options, WebpushFCMOptions):
            fcm_options = fcm_options.to_dict()

        if fcm_options:
            return messaging.WebpushFCMOptions(**fcm_options)
        else:
            return None

    def _compile_message(self, message: Union[Message, SimpleMessage]):
        message_dict = message.to_dict()

        token = message_dict.get("token")
        topic = None if token else message_dict.get("topic")
        data = self._process_data(message_dict.get("data"))

        return messaging.Message(
            data=data,
            webpush=self._compile_webpush_config(message_dict),
            fcm_options=self._compile_fcm_options(message_dict),
            token=token,
            topic=topic,
        )

    def _compile_multicast_message(self, message: MulticastMessage):
        message_dict = message.to_dict()

        return messaging.MulticastMessage(
            data=self._process_data(message_dict.get("data")),
            webpush=self._compile_webpush_config(message_dict),
            fcm_options=self._compile_fcm_options(message_dict),
            tokens=message_dict.get("tokens"),
        )

    def _process_data(self, data: dict) -> dict:
        if not isinstance(data, dict):
            return {}

        return {
            str(key): str(value)
            for key, value in data.items()
            if isinstance(key, (str, int, float))
            and isinstance(value, (str, int, float))
        }

    def _log(self, message: str) -> None:
        if self.with_logging:
            print(message)
