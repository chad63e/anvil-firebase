"""
Portable classes and helpers for Firebase Cloud Messaging (client-side).

Provides:
- Webpush notification models (actions, notification, webpush config)
- Message types (Message, MulticastMessage, SimpleMessage)
- Response types (Response, BatchResponse, TopicManagementResponse)

All classes are decorated with @anvil.server.portable_class for client/server transport.
"""

import anvil.server

from .client_utils import DataSerializer
from .validators import Validators

# MARK: Webpush entities


@anvil.server.portable_class
class FCMOptions:
    """Options for FCM analytics metadata associated with a message."""

    def __init__(self, analytics_label: str = None):
        """
        Initializes a new instance of the FCMOptions class.

        Args:
            analytics_label (str, optional): The label associated with the message’s analytics data. Defaults to None.
        """
        validator = Validators()
        self.analytics_label = validator.validate_string(
            analytics_label, "analytics_label", optional=True
        )

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"FCMOptions(analytics_label={self.analytics_label})"

    def to_dict(self):
        return DataSerializer.serialize(self, ["analytics_label"])


@anvil.server.portable_class
class WebpushNotificationAction:
    """Single action button definition for a webpush notification."""

    def __init__(self, action: str, title: str, icon: str = None):
        """
        Initializes a new instance of the WebpushNotificationAction class.

        Args:
            action (str): The action for the notification.
            title (str): The title for the notification.
            icon (str, optional): The icon for the notification. Defaults to None.
        """
        validator = Validators()
        self.action = validator.validate_string(action, "action")
        self.title = validator.validate_string(title, "title")
        self.icon = validator.validate_url(icon, "icon", optional=True)

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"WebpushNotificationAction(action={self.action}, title={self.title}, icon={self.icon})"

    def to_dict(self):
        return DataSerializer.serialize(self, ["action", "title", "icon"])


@anvil.server.portable_class
class WebpushNotification:
    """Notification content and behavior fields for webpush delivery."""

    def __init__(
        self,
        title: str = None,
        body: str = None,
        icon: str = None,
        actions: list = None,
        badge: str = None,
        data: dict = None,
        direction: str = "auto",
        image: str = None,
        language: str = None,
        renotify: bool = False,
        require_interaction: bool = False,
        silent: bool = False,
        tag: str = None,
        timestamp_millis: int = None,
        vibrate: list = None,
        custom_data: dict = None,
    ):
        """
        Initializes a new instance of the WebpushNotification class.

        Args:
            title (str, optional): Title of the notification. If specified, overrides the title set via messaging.Notification. Defaults to None.
            body (str, optional): Body of the notification. If specified, overrides the body set via messaging.Notification. Defaults to None.
            icon (str, optional): Icon URL of the notification. Defaults to None.
            actions (list[WebpushNotificationAction], optional): A list of actions to be displayed in the notification. Each action must be an instance of WebpushNotificationAction. Defaults to None.
            badge (str, optional): URL of the image used to represent the notification when there is not enough space to display the notification itself. Defaults to None.
            data (dict, optional): Any arbitrary JSON data that should be associated with the notification. Defaults to None.
            direction (str, optional): The direction in which to display the notification. Must be either ‘auto’, ‘ltr’ or ‘rtl’. Defaults to "auto".
            image (str, optional): The URL of an image to be displayed in the notification. Defaults to None.
            language (str, optional): Notification language. Defaults to None.
            renotify (bool, optional): A boolean indicating whether the user should be notified after a new notification replaces an old one. Defaults to False.
            require_interaction (bool, optional): A boolean indicating whether a notification should remain active until the user clicks or dismisses it, rather than closing automatically. Defaults to False.
            silent (bool, optional): True to indicate that the notification should be silent. Defaults to False.
            tag (str, optional): An identifying tag on the notification. Defaults to None.
            timestamp_millis (int, optional): A timestamp value in milliseconds on the notification. Defaults to None.
            vibrate (list[int], optional): A vibration pattern for the device’s vibration hardware to emit when the notification fires. The pattern is specified as an integer array. Defaults to None.
            custom_data (dict, optional): A dict of custom key-value pairs to be included in the notification. Defaults to None.
        """
        validator = Validators()

        self.title = validator.validate_string(title, "title", optional=True)
        self.body = validator.validate_string(body, "body", optional=True)
        self.icon = validator.validate_url(icon, "icon", optional=True)
        self.actions = validator.validate_list_of_specific_class(
            actions, "actions", cls=WebpushNotificationAction, optional=True
        )
        self.badge = validator.validate_url(badge, "badge", optional=True)
        self.data = validator.validate_dict(data, "data", optional=True)
        self.direction = validator.validate_string_options(
            direction, "direction", ["auto", "ltr", "rtl"], optional=True
        )
        self.image = validator.validate_url(image, "image", optional=True)
        self.language = validator.validate_string(language, "language", optional=True)
        self.renotify = validator.validate_bool(renotify, "renotify", optional=True)
        self.require_interaction = validator.validate_bool(
            require_interaction, "require_interaction", optional=True
        )
        self.silent = validator.validate_bool(silent, "silent", optional=True)
        self.tag = validator.validate_string(tag, "tag", optional=True)
        self.timestamp_millis = validator.validate_int(
            timestamp_millis, "timestamp_millis", optional=True
        )
        self.vibrate = validator.validate_list(vibrate, "vibrate", optional=True)
        self.custom_data = validator.validate_dict(
            custom_data, "custom_data", optional=True
        )

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"WebpushNotification(title={self.title})"

    def to_dict(self):
        return DataSerializer.serialize(
            self,
            [
                "title",
                "body",
                "icon",
                "actions",
                "badge",
                "data",
                "direction",
                "image",
                "language",
                "renotify",
                "require_interaction",
                "silent",
                "tag",
                "timestamp_millis",
                "vibrate",
                "custom_data",
            ],
        )


@anvil.server.portable_class
class WebpushFCMOptions:
    """Webpush-specific FCM options (e.g., link to open on click)."""

    def __init__(self, link: str = None):
        """
        Initializes a new instance of the WebpushFcmOptions class.

        Args:
            link (str, optional): The link to open when the user clicks on the notification. For all URL values, HTTPS is required. Defaults to None.
        """
        validator = Validators()
        self.link = validator.validate_url(link, "link", optional=True)

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"WebpushFCMOptions(link={self.link})"

    def to_dict(self):
        return DataSerializer.serialize(self, ["link"])


# MARK: - Webpush configuration


@anvil.server.portable_class
class WebpushConfig:
    """Webpush transport configuration: headers, data, notification, options."""

    def __init__(
        self,
        headers: dict = None,
        data: dict = None,
        notification: WebpushNotification = None,
        fcm_options: WebpushFCMOptions = None,
    ):
        """
        Initializes a new instance of the WebpushConfig class.

        Args:
            headers (dict): The headers for the Webpush message.
            data (dict, optional): The data for the Webpush message. Defaults to None.
            notification (dict, optional): The notification for the Webpush message. Defaults to None.
        """
        validator = Validators()
        self.headers = validator.validate_dict(headers, "headers", optional=True)
        self.data = validator.validate_dict(
            data, "data", strings_only=True, optional=True
        )
        self.notification = validator.validate_specific_class(
            notification, "notification", cls=WebpushNotification, optional=True
        )
        self.fcm_options = validator.validate_specific_class(
            fcm_options, "fcm_options", cls=WebpushFCMOptions, optional=True
        )

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"WebpushConfig: {id(self)}"

    def to_dict(self):
        return DataSerializer.serialize(
            self, ["headers", "data", "notification", "fcm_options"]
        )


# MARK: Message types


@anvil.server.portable_class
class Message:
    """Base message envelope for FCM with optional webpush config and data."""

    def __init__(
        self,
        data: dict = None,
        webpush: WebpushConfig = None,
        fcm_options: WebpushFCMOptions = None,
        token: str = None,
        topic: str = None,
        condition: str = None,
    ):
        """
        Initializes a new instance of the Message class.

        Args:
            data (dict, optional): The data for the message. Defaults to None.
            webpush (WebpushConfig, optional): The Webpush configuration for the message. Defaults to None.
            fcm_options (WebpushFCMOptions, optional): The FCM options for the message. Defaults to None.
            token (str, optional): The token for the message. Defaults to None.
            topic (str, optional): The topic for the message. Defaults to None.
            condition (str, optional): The condition for the message. Defaults to None.
        """
        validator = Validators()
        self.data = validator.validate_dict(
            data, "data", strings_only=True, optional=True
        )
        self.webpush = validator.validate_specific_class(
            webpush, "webpush", cls=WebpushConfig, optional=True
        )
        self.fcm_options = validator.validate_specific_class(
            fcm_options, "fcm_options", cls=WebpushFCMOptions, optional=True
        )
        self.token = validator.validate_string(token, "token", optional=True)
        self.topic = validator.validate_string(topic, "topic", optional=True)
        self.condition = validator.validate_string(
            condition, "condition", optional=True
        )

    @property
    def message_type(self):
        return "message"

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        title = self.webpush.notification.title if self.webpush else None
        return f"Message(title={title}): {id(self)}"

    def to_dict(self):
        return DataSerializer.serialize(
            self,
            [
                "data",
                "webpush",
                "fcm_options",
                "token",
                "topic",
                "condition",
            ],
        )


@anvil.server.portable_class
class MulticastMessage:
    """Message envelope targeting multiple registration tokens."""

    def __init__(
        self,
        data: dict = None,
        webpush: WebpushConfig = None,
        fcm_options: WebpushFCMOptions = None,
        tokens: list = None,
        condition: str = None,
    ):
        """
        Initializes a new instance of the MulticastMessage class.

        Args:
            data (dict, optional): The data for the message. Defaults to None.
            webpush (WebpushConfig, optional): The Webpush configuration for the message. Defaults to None.
            fcm_options (WebpushFCMOptions, optional): The FCM options for the message. Defaults to None.
            tokens (list[str], optional): The tokens for the message. Defaults to None.
            condition (str, optional): The condition for the message. Defaults to None.
        """
        validator = Validators()
        self.data = validator.validate_dict(
            data, "data", strings_only=True, optional=True
        )
        self.webpush = validator.validate_specific_class(
            webpush, "webpush", cls=WebpushConfig, optional=True
        )
        self.fcm_options = validator.validate_specific_class(
            fcm_options, "fcm_options", cls=WebpushFCMOptions, optional=True
        )
        self.tokens = validator.validate_list(tokens, "tokens", optional=True)
        self.condition = validator.validate_string(
            condition, "condition", optional=True
        )

    @property
    def message_type(self):
        return "multicast_message"

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        title = self.webpush.notification.title if self.webpush else None
        return f"MulticastMessage(title={title}): {id(self)}"

    def to_dict(self):
        return DataSerializer.serialize(
            self,
            [
                "data",
                "webpush",
                "fcm_options",
                "tokens",
                "condition",
            ],
        )


@anvil.server.portable_class
class SimpleMessage(Message):
    """Convenience message that builds a WebpushNotification from common fields."""

    def __init__(
        self,
        title: str,
        body: str,
        token: str = None,
        topic: str = None,
        condition: str = None,
        data: dict = None,
        custom_data: dict = None,
        headers: dict = None,
        icon: str = None,
        image: str = None,
        badge: str = None,
        link: str = None,
        actions: list = None,
        direction: str = "auto",
        language: str = None,
        renotify: bool = False,
        require_interaction: bool = False,
        silent: bool = False,
        tag: str = None,
        timestamp_millis: int = None,
        vibrate: list = None,
    ):
        """
        SimpleMessage is a subclass of the Message class. It represents a simple message that can be sent via Firebase Cloud Messaging.

        Parameters:
        title (str): The title of the notification.
        body (str): The body text of the notification.
        token (str, optional): The token of the device to send the notification to.
        topic (str, optional): The topic to send the notification to.
        condition (str, optional): The condition to send the notification to.
        data (dict, optional): A dictionary of data to send with the notification.
        custom_data (dict, optional): A dictionary of custom data to send with the notification.
        headers (dict, optional): A dictionary of headers to send with the notification.
        icon (str, optional): The URL of the icon image for the notification.
        image (str, optional): The URL of the image for the notification.
        badge (str, optional): The URL of the badge for the notification.
        link (str, optional): The link to open when the notification is clicked.
        actions (list, optional): A list of actions for the notification.
        direction (str, optional): The text direction of the notification. Defaults to 'auto'.
        language (str, optional): The language of the notification.
        renotify (bool, optional): Whether to renotify the user. Defaults to False.
        require_interaction (bool, optional): Whether user interaction is required. Defaults to False.
        silent (bool, optional): Whether the notification should be silent. Defaults to False.
        tag (str, optional): The tag of the notification.
        timestamp_millis (int, optional): The timestamp of the notification in milliseconds.
        vibrate (list, optional): A list of vibration patterns for the notification.
        """
        notification = WebpushNotification(
            title=title,
            body=body,
            icon=icon,
            actions=actions,
            badge=badge,
            direction=direction,
            image=image,
            language=language,
            renotify=renotify,
            require_interaction=require_interaction,
            silent=silent,
            tag=tag,
            timestamp_millis=timestamp_millis,
            vibrate=vibrate,
            custom_data=custom_data,
        )
        webpush = WebpushConfig(
            headers=headers,
            notification=notification,
            fcm_options=WebpushFCMOptions(link=link),
        )
        super(SimpleMessage, self).__init__(
            data=data, webpush=webpush, token=token, topic=topic, condition=condition
        )

    @property
    def message_type(self):
        return "simple_message"

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"FirebaseMessage(title={self.title})"

    def to_dict(self):
        return DataSerializer.serialize(
            self,
            [
                "data",
                "webpush",
                "fcm_options",
                "token",
                "topic",
                "condition",
            ],
        )


# MARK: Response types


@anvil.server.portable_class
class Response:
    """Result of sending a single FCM message (success/id or exception)."""

    def __init__(self, success: bool, message_id: str = None, exception: str = None):
        """
        Initializes a new instance of the Response class.

        Args:
            message_id (str): The message ID.
            success (bool): Whether the message was sent successfully.
            exception (str, optional): The exception that occurred. Defaults to None.
        """
        validator = Validators()
        self.success = validator.validate_bool(success, "success")
        self.message_id = validator.validate_string(
            message_id, "message_id", optional=True
        )
        self.exception = validator.validate_string(
            exception, "exception", optional=True
        )

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        if self.success:
            return f"Response(message_id={self.message_id}, success={self.success})"
        else:
            return f"Response(exception={self.exception}, success={self.success})"

    @classmethod
    def from_fcm_response(cls, response):
        # Initialize default values
        success = False
        message_id = None
        exception = None

        if isinstance(response, str):
            parts = response.split("/messages/")
            if len(parts) >= 2:
                message_id = parts[1]
                success = True
        elif isinstance(response, Exception):
            exception = str(response)
        else:
            # Try to extract success, message_id, and exception from response
            success = cls._extract_success(response)
            message_id = cls._extract_attribute(response, "message_id")
            exception = cls._extract_attribute(
                response, "exception"
            ) or cls._extract_attribute(response, "error")
            if not isinstance(exception, (str, type(None))):
                try:
                    exception = str(exception)
                except Exception:
                    exception = None

        return cls(success=success, message_id=message_id, exception=exception)

    @classmethod
    def _extract_success(cls, response):
        try:
            success = response.success
            if isinstance(success, str):
                return success.lower() in ["1", "true"]
            elif isinstance(success, int):
                return success == 1
        except Exception:
            pass
        return False

    @classmethod
    def _extract_attribute(cls, response, attribute):
        try:
            return getattr(response, attribute)
        except Exception:
            return None


@anvil.server.portable_class
class BatchResponse:
    """Aggregate result for multicast/batch sends (counts and per-item results)."""

    def __init__(self, responses: list, success_count: int, failure_count: int):
        """
        Initializes a new instance of the BatchResponse class.

        Args:
            responses (list[Response]): The list of responses.
            success_count (int): The number of successful responses.
            failure_count (int): The number of failed responses.
        """
        validator = Validators()
        self.responses = validator.validate_list(
            responses, "responses", strings_only=False
        )
        self.success_count = validator.validate_int(success_count, "success_count")
        self.failure_count = validator.validate_int(failure_count, "failure_count")

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"BatchResponse(success_count={self.success_count}, failure_count={self.failure_count})"

    @classmethod
    def from_fcm_response(cls, response):
        try:
            resp_items = response.responses
        except Exception:
            resp_items = []

        try:
            success_count = response.success_count
        except Exception:
            success_count = 0

        try:
            failure_count = response.failure_count
        except Exception:
            failure_count = 0

        process_responses = [Response.from_fcm_response(r) for r in resp_items]

        return cls(
            process_responses,
            success_count,
            failure_count,
        )


@anvil.server.portable_class
class TopicManagementResponse:
    """Result of subscribing/unsubscribing to a topic (counts and errors)."""

    def __init__(self, success_count: int, failure_count: int, errors: list):
        """
        Initializes a new instance of the TopicManagementResponse class.

        Args:
            success_count (int): The number of successful responses.
            failure_count (int): The number of failed responses.
            errors (list): The list of errors.
        """
        validator = Validators()
        self.success_count = validator.validate_int(success_count, "success_count")
        self.failure_count = validator.validate_int(failure_count, "failure_count")
        self.errors = validator.validate_list(errors, "errors")

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"TopicManagementResponse(success_count={self.success_count}, failure_count={self.failure_count})"

    @classmethod
    def from_fcm_response(cls, response):
        return cls(
            response.success_count,
            response.failure_count,
            response.errors,
        )
