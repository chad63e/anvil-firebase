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