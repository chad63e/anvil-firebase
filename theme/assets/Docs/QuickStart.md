# Quick Start Guide: Setting Up Firebase Messaging in Anvil

This guide provides a comprehensive setup for integrating Firebase Messaging into an Anvil application, covering both the Firebase Console configuration and Anvil client/server-side setup.

## Guide Outline
1. [Setting Up Firebase Project in Firebase Console](#part-1-setting-up-firebase-project-in-firebase-console)
   - [Create a Firebase Project](#step-1-create-a-firebase-project)
   - [Get Firebase Config Dictionary](#step-2-get-firebase-config-dictionary)
   - [Obtain VAPID Key](#step-3-obtain-vapid-key)
   - [Download Service Account JSON](#step-4-download-service-account-json)
   - [Set Up Service Worker in Anvil Assets](#step-5-set-up-service-worker-in-anvil-assets)
2. [Setup Service Worker](#part-2-service-worker-setup)
3. [Client-Side Setup in Anvil Main Form](#part-3-client-side-setup-in-anvil-main-form)
   - [Example Anvil Form Code](#example-anvil-form-code)
4. [Server-Side Interaction in Anvil](#part-4-server-side-interaction-in-anvil)
   - [Server Code Example](#server-code-example)
5. [Conclusion](#conclusion)

---

## Part 1: Setting Up Firebase Project in Firebase Console
### Step 1: Create a Firebase Project
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click "Add project" and follow the steps to create a new Firebase project.

### Step 2: Get Firebase Config Dictionary
1. In the Firebase Console, select your project.
2. Click on the gear icon (⚙️) and go to "Project settings".
3. Under "Your apps", select or create a Web app.
4. Find your Firebase configuration object with keys like `apiKey`, `authDomain`, etc.

### Step 3: Obtain VAPID Key
1. In the "Cloud Messaging" tab of your project settings, find the Web Push certificates.
2. Generate a key pair. This is your VAPID key.

### Step 4: Download Service Account JSON
1. Go to the "Service accounts" tab in your project settings.
2. Click "Generate new private key" and download the JSON file.

[Back to Top](#quick-start-guide-setting-up-firebase-messaging-in-anvil)

## Part 2: Service Worker Setup

### Set Up Service Worker in Anvil Assets
1. In Anvil IDE, go to "Assets" and add a new file named `fb-service-worker.js`.
2. Copy and paste the provided service worker code into this file.
3. This file is crucial for handling Firebase notifications.
- Notes: 
  - While it's possible to use your own service worker, if you choose to utilize `ActionMap` and `FirebaseClient.add_action_map`, you'll need to incorporate the associated handling code as outlined below.
  - If your service worker is not named `fb-service-worker.js`, or if it's located outside of the Anvil assets directory, you'll need to specify the `service_worker_url` when initializing the `FirebaseClient`.

<details>
<summary>SERVICE WORKER CODE:</summary>

```javascript
// Import the Firebase scripts
importScripts('https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.10.1/firebase-messaging.js');


// Initialize Firebase Notification Actions Map
let actionMaps = {};


// Add event listeners
self.addEventListener('message', handleMessageEvent);
self.addEventListener('notificationclick', handleNotificationClickEvent);


/**
 * Handles incoming messages from the main thread.
 * 
 * @param {MessageEvent} event - The message event.
 * 
 * If the message type is 'SET_FIREBASE_CONFIG', it initializes Firebase with the provided configuration.
 * If the message type is 'ADD_ACTION_MAP', it adds a new action map with the provided details.
 * The action map includes the URL, parameters, data, and Bearer authorization key for the action.
 * 
 * Any errors that occur during the handling of the message event are caught and logged to the console.
 */
function handleMessageEvent(event) {
    try {
        if (event.data.type === 'SET_FIREBASE_CONFIG') {
            initializeFirebase(event.data.firebaseConfig);
        } else if (event.data.type === 'ADD_ACTION_MAP') {
            actionMaps[event.data.actionName] = {
                url: event.data.fullUrl,
                params: event.data.params,
                data: event.data.data,
                authKey: event.data.authKey,
            };
        }
    } catch (error) {
        console.error(`Error handling message event: ${error}`);
    }
}


/**
 * Handles click events on notifications.
 * 
 * @param {NotificationEvent} event - The notification event.
 * 
 * The function prevents the default action, retrieves the action name, FCM message ID, and sender ID from the notification data,
 * and if an action map for the action name exists, it handles the action. Finally, it closes the notification.
 */
function handleNotificationClickEvent(event) {
    event.preventDefault();

    const actionName = event.action;
    const fcmMessageId = event.notification.data.fcmMessageId;
    const fromId = event.notification.data.from;

    if (actionMaps[actionName]) {
        event.waitUntil(handleAction(actionName, fcmMessageId, fromId));
    }

    event.notification.close();
}


/**
 * Handles the specified action.
 * 
 * @param {string} actionName - The name of the action to handle.
 * @param {string} fcmMessageId - The Firebase Cloud Messaging message ID.
 * @param {string} fromId - The sender ID.
 * 
 * The function retrieves the action from the action maps using the action name. If the action is not found, it logs an error and returns.
 * If the action's URL includes '/_/api/', it calls `handleServerUrl` with the action, FCM message ID, and sender ID.
 * Otherwise, it calls `handleClientUrl` with the action.
 */
function handleAction(actionName, fcmMessageId, fromId) {
    const action = actionMaps[actionName];

    if (!action) {
        console.error(`Action not found: ${actionName}`);
        return;
    }

    const { url } = action;

    if (url.includes('/_/api/')) {
        handleServerUrl(action, fcmMessageId, fromId);
    } else {
        handleClientUrl(action);
    }
}


/**
 * Handles server URLs by making a POST request to the specified URL.
 * 
 * @param {Object} action - The action object containing the URL, authorization key, data, and parameters.
 * @param {string} fcmMessageId - The Firebase Cloud Messaging message ID.
 * @param {string} fromId - The sender ID.
 * 
 * The function creates a URL object from the action's URL and adds any parameters to the URL.
 * It then makes a POST request to the URL with the FCM message ID, sender ID, and any additional data from the action.
 * If the action includes an authorization key, it is included as a Bearer token in the 'Authorization' header of the request.
 * If an error occurs during the fetch operation, it is logged to the console.
 */
function handleServerUrl(action, fcmMessageId, fromId) {
    const { url, authKey, data, params } = action;

    var headers = {
        'Content-Type': 'application/json'
    };

    if (authKey) {
        headers['Authorization'] = `Bearer ${authKey}`;
    }

    // Create a URL object
    let urlObj = new URL(url);

    // Add params to the URL
    if (params) {
        Object.keys(params).forEach(key => urlObj.searchParams.append(key, params[key]));
    }

    fetch(urlObj.toString(), {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ fcmMessageId, fromId, ...data })
    })
        .catch(error => {
            console.error('Error calling server URL:', error);
        });
}


/**
 * Handles client URLs by opening a new window with the specified URL.
 * 
 * @param {Object} action - The action object containing the URL.
 * 
 * The function creates a new URL object from the action's URL and the service worker's location origin.
 * It then attempts to open a new window with this URL.
 * If an error occurs during the window opening operation, it is logged to the console.
 */
function handleClientUrl(action) {
    const url = new URL(action.url, self.location.origin).href;

    clients.openWindow(url).catch(error => {
        console.error('Error opening new window:', error);
    });
}


/**
 * Initializes Firebase with the provided configuration.
 * 
 * @param {Object} firebaseConfig - The Firebase configuration object.
 * 
 * The function checks if Firebase has already been initialized. If not, it initializes Firebase with the provided configuration.
 * The configuration object should include the API key, auth domain, project ID, storage bucket, messaging sender ID, app ID, and measurement ID.
 * After initializing Firebase, it calls `initializeFirebaseMessaging` to initialize Firebase Messaging.
 */
function initializeFirebase(firebaseConfig) {
    if (!firebase.apps.length) {
        firebase.initializeApp({
            apiKey: firebaseConfig.apiKey,
            authDomain: firebaseConfig.authDomain,
            projectId: firebaseConfig.projectId,
            storageBucket: firebaseConfig.storageBucket,
            messagingSenderId: firebaseConfig.messagingSenderId,
            appId: firebaseConfig.appId,
            measurementId: firebaseConfig.measurementId,
        });

        initializeFirebaseMessaging();
    }
}


/**
 * Initializes Firebase Messaging and sets the background message handler.
 * 
 * The function retrieves the Firebase Messaging instance and sets the background message handler to `handleBackgroundMessage`.
 * This function should be called after Firebase has been initialized.
 */
function initializeFirebaseMessaging() {
    const messaging = firebase.messaging();

    messaging.setBackgroundMessageHandler(handleBackgroundMessage);
}


/**
 * Handles background messages by showing a notification.
 * 
 * @param {Object} payload - The message payload.
 * 
 * The function retrieves the title from the payload data, defaulting to 'New Message' if no title is provided.
 * It then creates a notification options object from the payload data and shows a notification with the title and options.
 * This function is intended to be used as a background message handler for Firebase Messaging.
 */
function handleBackgroundMessage(payload) {
    const title = payload.data.title || 'New Message';
    const options = { ...payload.data };

    return self.registration.showNotification(title, options);
}
```
</details>

#### Note:
This service worker dynamically loads the Firebase configuration and actions. It does this by listening for incoming messages from the main thread. When a message arrives, the service worker checks if it contains an action map. If it does, the service worker updates its internal action map with the new actions. These actions can include redirections or POST requests to API URLs. When a notification is clicked, the service worker checks its action map for the corresponding action and executes it. This dynamic loading of actions allows for flexible and responsive handling of notification interactions.

[Back to Top](#quick-start-guide-setting-up-firebase-messaging-in-anvil)

## Part 3: Client-Side Setup in Anvil Main Form

### Example Anvil Form Code
Below is an example of how to set up Firebase in the client side of an Anvil app. It's important to initialize Firebase after the Dom window is fully loaded to ensure all elements are rendered and ready.

```python
from anvil import *
import anvil.js
from Firebase.client import FirebaseClient, FirebaseConfig

PUBLIC_VAPID_KEY = "your_public_vapid_key"
# You could also save this in an Anvil Secret and call it on load.

class MainForm(MainFormTemplate):

    def __init__(self, **properties):
        self.init_components(**properties)

        # Ensure the Dom window is fully loaded
        anvil.js.window.addEventListener('load', self.initialize_firebase)

    def initialize_firebase(self, *args):
        firebase_config = FirebaseConfig(
            api_key="your-api-key",
            auth_domain="your-auth-domain",
            # ... other config parameters
        )

        # Initialize Firebase Client
        self.firebase_client = FirebaseClient(
            config=firebase_config
            public_vapid_key=PUBLIC_VAPID_KEY,
            message_handler=self.message_handler, # Optional
            subscribe_handler=self.subscribe_handler, # Optional
            unsubscribe_handler=self.subscribe_handler, # Optional
            )

        # Initialize Firebase App
        self.firebase_client.initialize_app()

        # Request Notification Permission
        self.request_notification_permission()

    def request_notification_permission(self):
        if self.firebase_client.request_notification_permission():
            Notification("Notification permission granted.").show()
        else:
            Notification("Notification permission denied.").show()

    def message_handler(self, payload):
        print(f"Message Payload Recieved: {payload}")

    def subscribe_handler(self, topic, token):
        response = anvil.server.call("subscribe_to_topic", topic, token)
        # This will return a TopicManagementResponse object

        print(response)

    def unsubscribe_handler(self, topic, token):
        response = anvil.server.call("unsubscribe_from_topic", topic, token)
        # This will return a TopicManagementResponse object

        print(response)

    # Add more event handlers and functions as needed
```

[Back to Top](#quick-start-guide-setting-up-firebase-messaging-in-anvil)

## Part 4: Server-Side Interaction in Anvil

### Server Code Example
Here's how you can interact with Firebase on the server side. Remember to instantiate `FirebaseMessaging` in each callable function, unless using a persistent server.

```python
import anvil.secrets
import anvil.server

from Firebase.messages import Message, MulticastMessage
from Firebase.server import FCMServiceAccountCredentials, FirebaseMessaging

# This setup assumes you are saving your Firebase Service Account JSON in an Anvil Secret
FCM_SERVICE_ACCOUNT_JSON = anvil.secrets.get_secret("FCM_SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_CREDS = FCMServiceAccountCredentials.from_json_string(
    FCM_SERVICE_ACCOUNT_JSON
)

# Initialize Firebase Messaging
messaging = FirebaseMessaging()
messaging.initialize_firebase_admin(SERVICE_ACCOUNT_CREDS)

@anvil.server.callable
def subscribe_to_topic(topic, token):
    # subscribe to topic
    return messaging.subscribe_to_topic(topic, token)

@anvil.server.callable
def unsubscribe_to_topic(topic, token):
    # unsubscribe to topic
    return messaging.unsubscribe_from_topic(topic, token)

@anvil.server.callable
def send_message_to_user(user_token):
    # Create a message
    message = Message(
        data={"title": "Hello", "body": "Welcome to Firebase Messaging!"},
        token=user_token
    )

    # Send the message
    response = messaging.send(message)

    if response.success:
        return f"Message sent successfully: {response.message_id}"
    else:
        return f"Failed to send message: {response.exception}"
```

## Conclusion
This guide provides a quick setup process for Firebase Messaging in an Anvil application, covering both client-side and server-side implementations. It ensures a smooth integration of Firebase into your Anvil app, enabling advanced messaging and notification features.

[Back to Top](#quick-start-guide-setting-up-firebase-messaging-in-anvil)