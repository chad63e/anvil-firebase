# Firebase Cloud Messaging for Anvil — User Guide

This app integrates Firebase Cloud Messaging (FCM) with Anvil. It provides:

- Portable client/server message models (`messages.py`) aligned with FCM Webpush.
- A server-side wrapper (`FirebaseMessaging`) around `firebase_admin.messaging`.
- A preconfigured service worker under `theme/assets/fb-service-worker.js`.

Use it to send push notifications to devices, manage topics, and control Webpush options from Anvil.

## Quick Start

1. Configure a Firebase service account and copy the JSON contents.
2. In the Anvil Editor, add a Secret named `FIREBASE_SERVICE_ACCOUNT_JSON` and paste the JSON string.
3. In a server module, initialize Firebase Admin and send a test message:

```python
from .server_utils import FCMServiceAccountCredentials
from .server import FirebaseMessaging
from .messages import SimpleMessage, WebpushConfig, WebpushNotification
import anvil.secrets

fm = FirebaseMessaging()
creds_json = anvil.secrets.get_secret("FIREBASE_SERVICE_ACCOUNT_JSON")
creds = FCMServiceAccountCredentials.from_json_string(creds_json)
fm.initialize_firebase_admin(creds)

# Send to a single token
msg = SimpleMessage(
    token="FCM_DEVICE_TOKEN",
    data={"example": "hello"},
    webpush=WebpushConfig(
        notification=WebpushNotification(title="Hello", body="World")
    ),
)
resp = fm.send(msg)
print(resp)  # Inspect result on the server log
```

## Usage Examples

### Subscribe/Unsubscribe to Topics

```python
fm.subscribe_to_topic("news", token)
fm.unsubscribe_from_topic("news", token)
```

### Send Multiple Messages (Batch)

```python
from .messages import Message

messages = [
    Message(token=t, data={"k": "v"})
    for t in ["token1", "token2"]
]
batch = fm.send_all(messages)
print(batch)
```

### Send Multicast Message

```python
from .messages import MulticastMessage

multi = MulticastMessage(
    tokens=["token1", "token2"],
    data={"k": "v"},
)
batch = fm.send_multicast(multi)
```

## Notes and Troubleshooting

- Ensure your service account has permission to use FCM.
- Tokens must be current/valid; handle client token refresh appropriately.
- The service worker at `theme/assets/fb-service-worker.js` handles Webpush events.
- Data payload values are coerced to strings by the server for FCM compliance.

## Browser Compatibility (Microsoft Edge)

- Supported: Chromium-based Edge 79+.
- Not supported: Legacy Edge (EdgeHTML).
- Permissions: Allow Notifications for your site (edge://settings/content/notifications). Windows Focus Assist/Do Not Disturb can suppress toasts; check the Action Center if you do not see a banner.
- Service worker scope: This app serves the worker at `/_/theme/fb-service-worker.js` and binds it with `messaging.useServiceWorker(...)`, which is supported in Edge.
- VAPID key: Edge requires `applicationServerKey` to be a Uint8Array. The client library handles this automatically. If testing manually with `PushManager.subscribe(...)`, convert your base64url public VAPID key to a Uint8Array first.
- InPrivate: InPrivate windows can restrict service worker persistence and notifications. Test in a normal profile.
- Updating the worker: After edits, reload the app or use DevTools → Application → Service Workers to "Update"/"Skip waiting". You can also unregister and reload.

Troubleshooting on Edge:

- Verify a service worker is active (DevTools → Application → Service Workers).
- Confirm `navigator.serviceWorker.ready` resolves and the registration scope includes `/_/theme/`.
- Check the Console for errors (DevTools, or edge://serviceworker-internals).
- If `InvalidAccessError` occurs when subscribing, regenerate the Web Push VAPID key and make sure you are using the Firebase Cloud Messaging Web Push public key.

---

# About This [Anvil](https://anvil.works/?utm_source=github:app_README) App

### Build web apps with nothing but Python.

The app in this repository is built with [Anvil](https://anvil.works?utm_source=github:app_README), the framework for building web apps with nothing but Python. You can clone this app into your own Anvil account to use and modify.

Below, you will find:
- [How to open this app](#opening-this-app-in-anvil-and-getting-it-online) in Anvil and deploy it online
- Information [about Anvil](#about-anvil)
- And links to some handy [documentation and tutorials](#tutorials-and-documentation)

## Opening this app in Anvil and getting it online

### Cloning the app

Go to the [Anvil Editor](https://anvil.works/build?utm_source=github:app_README) (you might need to sign up for a free account) and click on “Clone from GitHub” (underneath the “Blank App” option):

<img src="https://anvil.works/docs/version-control-new-ide/img/git/clone-from-github.png" alt="Clone from GitHub"/>

Enter the URL of this GitHub repository. If you're not yet logged in, choose "GitHub credentials" as the authentication method and click "Connect to GitHub".

<img src="https://anvil.works/docs/version-control-new-ide/img/git/clone-app-from-git.png" alt="Clone App from Git modal"/>

Finally, click "Clone App".

This app will then be in your Anvil account, ready for you to run it or start editing it! **Any changes you make will be automatically pushed back to this repository, if you have permission!** You might want to [make a new branch](https://anvil.works/docs/version-control-new-ide?utm_source=github:app_README).

### Running the app yourself:

Find the **Run** button at the top-right of the Anvil editor:

<img src="https://anvil.works/docs/img/run-button-new-ide.png"/>


### Publishing the app on your own URL

Now you've cloned the app, you can [deploy it on the internet with two clicks](https://anvil.works/docs/deployment/quickstart?utm_source=github:app_README)! Find the **Publish** button at the top-right of the editor:

<img src="https://anvil.works/docs/deployment-new-ide/img/environments/publish-button.png"/>

When you click it, you will see the Publish dialog:

<img src="https://anvil.works/docs/deployment-new-ide/img/quickstart/empty-environments-dialog.png"/>

Click **Publish This App**, and you will see that your app has been deployed at a new, public URL:

<img src="https://anvil.works/docs/deployment-new-ide/img/quickstart/default-public-environment.png"/>

That's it - **your app is now online**. Click the link and try it!

## About Anvil

If you’re new to Anvil, welcome! Anvil is a platform for building full-stack web apps with nothing but Python. No need to wrestle with JS, HTML, CSS, Python, SQL and all their frameworks – just build it all in Python.

<figure>
<figcaption><h3>Learn About Anvil In 80 Seconds👇</h3></figcaption>
<a href="https://www.youtube.com/watch?v=3V-3g1mQ5GY" target="_blank">
<img
  src="https://anvil-website-static.s3.eu-west-2.amazonaws.com/anvil-in-80-seconds-YouTube.png"
  alt="Anvil In 80 Seconds"
/>
</a>
</figure>
<br><br>

[![Try Anvil Free](https://anvil-website-static.s3.eu-west-2.amazonaws.com/mark-complete.png)](https://anvil.works?utm_source=github:app_README)

To learn more about Anvil, visit [https://anvil.works](https://anvil.works?utm_source=github:app_README).

## Tutorials and documentation

### Tutorials

If you are just starting out with Anvil, why not **[try the 10-minute Feedback Form tutorial](https://anvil.works/learn/tutorials/feedback-form?utm_source=github:app_README)**? It features step-by-step tutorials that will introduce you to the most important parts of Anvil.

Anvil has tutorials on:
- [Building Dashboards](https://anvil.works/learn/tutorials/data-science#dashboarding?utm_source=github:app_README)
- [Multi-User Applications](https://anvil.works/learn/tutorials/multi-user-apps?utm_source=github:app_README)
- [Building Web Apps with an External Database](https://anvil.works/learn/tutorials/external-database?utm_source=github:app_README)
- [Deploying Machine Learning Models](https://anvil.works/learn/tutorials/deploy-machine-learning-model?utm_source=github:app_README)
- [Taking Payments with Stripe](https://anvil.works/learn/tutorials/stripe?utm_source=github:app_README)
- And [much more....](https://anvil.works/learn/tutorials?utm_source=github:app_README)

### Reference Documentation

The Anvil reference documentation provides comprehensive information on how to use Anvil to build web applications. You can find the documentation [here](https://anvil.works/docs/overview?utm_source=github:app_README).

If you want to get to the basics as quickly as possible, each section of this documentation features a [Quick-Start Guide](https://anvil.works/docs/overview/quickstarts?utm_source=github:app_README).
