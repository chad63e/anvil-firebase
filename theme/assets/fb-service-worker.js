/**
 * Firebase Cloud Messaging (FCM) Service Worker for Anvil
 *
 * Responsibilities:
 * - Initialize Firebase v8 Messaging in the service worker context.
 * - Receive configuration and action maps from the client via postMessage.
 * - Display background notifications and handle notification action clicks.
 * - Fast-activate on install and claim existing clients on activate.
 *
 * Notes:
 * - This worker is served under `/_/theme/` in Anvil, which is acceptable for FCM background
 *   notifications when the client binds messaging to this registration via `messaging.useServiceWorker(...)`.
 * - Uses the Firebase Web SDK v8 API (`setBackgroundMessageHandler`) for current compatibility.
 */

// Import the Firebase scripts
importScripts('https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.10.1/firebase-messaging.js');


// MARK: State

// Initialize Firebase Notification Actions Map
let actionMaps = {};


// MARK: Lifecycle & event listeners

self.addEventListener('install', (event) => {
    self.skipWaiting();
});
self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});
self.addEventListener('message', handleMessageEvent);
self.addEventListener('notificationclick', handleNotificationClickEvent);
// Register push-related handlers at initial evaluation to satisfy browser requirements.
self.addEventListener('push', handlePushEvent);
self.addEventListener('pushsubscriptionchange', handlePushSubscriptionChangeEvent);


// MARK: - Types

/**
 * @typedef {Object} ActionMap
 * @property {string} url - Absolute or relative URL to execute for this action.
 * @property {Object<string, string>} [params] - Query parameters appended to the URL (non-API flows).
 * @property {Object<string, any>} [data] - JSON body merged with FCM identifiers (API flows).
 * @property {string} [authKey] - Bearer token used as `Authorization: Bearer <authKey>` for API calls.
 */

/**
 * @typedef {Object} FirebaseConfig
 * @property {string} apiKey
 * @property {string} authDomain
 * @property {string} projectId
 * @property {string} storageBucket
 * @property {string} messagingSenderId
 * @property {string} appId
 * @property {string} [measurementId]
 */

// MARK: - Message channel handlers

/**
 * Handle messages from controlled clients (window contexts).
 *
 * Recognized message shapes:
 * - { type: 'SET_FIREBASE_CONFIG', firebaseConfig: FirebaseConfig }
 * - { type: 'ADD_ACTION_MAP', actionName: string, fullUrl: string, params?: Object, data?: Object, authKey?: string }
 *
 * @param {MessageEvent} event - postMessage payload from a controlled client.
 * @returns {void}
 *
 * Errors are caught and logged to avoid terminating the service worker event.
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


// MARK: - Notification click handling

/**
 * Handle click events on displayed notifications.
 *
 * Uses event.waitUntil(...) to extend the lifetime while the async action runs.
 * The notification data is expected to contain { fcmMessageId, from } as provided by FCM.
 *
 * @param {NotificationEvent} event
 * @returns {void}
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


// MARK: - Push event handlers

/**
 * Handle 'push' events by delegating to the background message handler.
 * Ensures the handler is present at initial evaluation time without relying on
 * late-installed Firebase messaging listeners.
 *
 * @param {PushEvent} event
 * @returns {void}
 */
function handlePushEvent(event) {
    try {
        const payload = event.data ? event.data.json() : {};
        event.waitUntil(handleBackgroundMessage(payload));
    } catch (error) {
        console.error('Error handling push event:', error);
    }
}

/**
 * Handle 'pushsubscriptionchange' events. This implementation logs the event.
 * Re-subscription logic can be added if a VAPID key is available in worker scope.
 *
 * @param {PushSubscriptionChangeEvent} event
 * @returns {void}
 */
function handlePushSubscriptionChangeEvent(event) {
    // No-op; add re-subscribe logic here if desired.
    // Keeping a listener registered at initial evaluation prevents browser warnings.
    console.log('pushsubscriptionchange event detected');
}


// MARK: - Action routing

/**
 * Resolve an action name to an ActionMap and perform it.
 *
 * - API URLs (containing '/_/api/') trigger a POST via handleServerUrl.
 * - Other URLs open a client window via handleClientUrl.
 *
 * @param {string} actionName
 * @param {string} fcmMessageId
 * @param {string} fromId
 * @returns {Promise<void>} Settles when the action completes or is skipped.
 */
function handleAction(actionName, fcmMessageId, fromId) {
    const action = actionMaps[actionName];

    if (!action) {
        console.error(`Action not found: ${actionName}`);
        return Promise.resolve();
    }

    const { url } = action;

    if (url.includes('/_/api/')) {
        return handleServerUrl(action, fcmMessageId, fromId);
    } else {
        return handleClientUrl(action);
    }
}


// MARK: - Server/API action

/**
 * Handle server/API action via POST to the specified URL.
 *
 * @param {ActionMap} action - The action details including URL and optional token/body/params.
 * @param {string} fcmMessageId - Firebase Cloud Messaging message ID.
 * @param {string} fromId - Sender ID (from payload).
 * @returns {Promise<void>} Resolves after the fetch completes (errors are logged and swallowed).
 *
 * Creates a URL with optional query params, sets JSON headers and optional Bearer auth, then POSTs a JSON body
 * containing { fcmMessageId, fromId, ...action.data }.
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

    return fetch(urlObj.toString(), {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ fcmMessageId, fromId, ...data })
    }).catch(error => {
        console.error('Error calling server URL:', error);
    });
}


// MARK: - Client/window action

/**
 * Handle client URL by opening a new window (or focusing an existing one if supported).
 *
 * @param {ActionMap} action - The action object containing the URL.
 * @returns {Promise<void>} Resolves after attempting to open a window (errors are logged and swallowed).
 *
 * Creates a fully-qualified URL relative to this worker's origin and uses clients.openWindow.
 */
function handleClientUrl(action) {
    const url = new URL(action.url, self.location.origin).href;

    return clients.openWindow(url).catch(error => {
        console.error('Error opening new window:', error);
    });
}


// MARK: - Firebase initialization

/**
 * Initialize Firebase with the provided configuration.
 *
 * @param {FirebaseConfig} firebaseConfig - Firebase configuration from the client.
 * @returns {void}
 *
 * No-op if Firebase was already initialized. After initialization, configures messaging handlers.
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
    }
}


// MARK: - Messaging bootstrap

/**
 * Initialize Firebase Messaging and set the background message handler.
 *
 * @returns {void}
 *
 * Uses the v8 messaging instance, configuring `setBackgroundMessageHandler`.
 */
function initializeFirebaseMessaging() {
    const messaging = firebase.messaging();

    messaging.setBackgroundMessageHandler(handleBackgroundMessage);
}


// MARK: - Background messaging

/**
 * Handle background messages by showing a notification.
 *
 * @param {Object} payload - Raw FCM payload; expects `data` with notification fields.
 * @returns {Promise<void>} Resolves after the notification is shown.
 *
 * Derives the notification title from `payload.data.title` and passes the remaining fields as options.
 */
function handleBackgroundMessage(payload) {
    const data = (payload && payload.data) ? payload.data : {};
    const notification = (payload && payload.notification) ? payload.notification : {};

    const title = data.title || notification.title || 'New Message';
    const options = { ...notification, ...data };

    return self.registration.showNotification(title, options);
}