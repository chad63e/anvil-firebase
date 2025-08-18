# Changelog

All notable changes to this project will be documented in this file.
This project adheres to Keep a Changelog format and Semantic Versioning where practical.

## [1.0.4] - 2025-08-18

### Added

- Documentation and code comments across client and server modules:
  - `client_code/client_utils.py`, `client_code/client.py`, `client_code/validators.py`, `client_code/messages.py`
  - `server_code/server.py`, `server_code/server_utils.py`
- Structured `# MARK:` and `# MARK: -` sections to organize code.
- Module docstrings and concise class/method docstrings to clarify responsibilities and usage.
- README updated with a User Guide (Quick Start, configuration, and usage examples).

### Changed

- Corrected public method docstrings in `server_code/server.py` to reference portable types and correct unions.
- Replaced accidental `// MARK:` with Python `# MARK:` comments.
- `client_code/client.py`: Centralized notification permission UX. Shows an interactive alert with an "Enable now" button only when permission is `default`; for `denied`, shows a passive `Notification` (see Fixed below for loop prevention details).
- On permission `granted`, the client wires ActionMaps and immediately attempts to retrieve and save the device token.
- Service worker registration is no longer overridden by `navigator.serviceWorker.ready`. We keep the specific registration returned by `register(self.service_worker_url)` to avoid binding to a non-Firebase/global SW in the IDE.
- `messaging.getToken(...)` is now called with the `serviceWorkerRegistration` option when available, improving reliability of token association with the registered SW.
- Added logging before token retrieval indicating whether a VAPID key is configured.
- Improved token retrieval stability (previous `AbortError: Registration failed - push service error`): retain our Firebase SW registration instead of the global `ready` registration and pass the SW registration into `getToken`; skip topic subscription until a token is present and subscribe right after saving it.

### Fixed

- Addressed a lint warning (Ruff F841) in `client_code/messages.py` by avoiding variable shadowing in `BatchResponse.from_fcm_response()`.
- Ensured `BatchResponse.from_fcm_response()` compiles entries from the collected response list consistently (internal cleanup; no external behavior change).
- Guarded `client_code/client.py` `_add_action_maps_to_service_worker()` against `None` `action_maps` to prevent a potential `TypeError` during permission grant.
- `request_notification_permission()` now returns the final permission status after any interactive re-prompt (reads `Notification.permission`), ensuring accurate boolean results.
- Prevented interactive alert loop by only prompting when permission is `default`; for `denied`, show a passive `Notification` and stop re-requesting.

### Notes

- Behavior change: users see an interactive prompt instead of only a passive notification on denied/default permission states.
- App code can rely on the library for permission prompting and token retrieval; remove redundant app-level prompts if present.
- Continues to follow the Unicode Symbol Policy (no Unicode in print statements) and Ruff linting configuration.
- If token retrieval still fails with a push service error, verify that your Web Push (VAPID) public key matches the Firebase project configured in `FirebaseConfig`.

## [1.0.3] - 2024-03-27

### Changed

- Update how an exception is processed in `Response` of a `BatchResponse`.

### Fixed

- Edited messages and validators.

## [1.0.2] - 2024-03-03

### Changed

- Updated how the Service Worker registration is fetched when performing `postMessage()` to ensure the correct registration instance is used.

### Notes

- Minor maintenance and cleanup.

## [1.0.1] - 2024-01-29

### Added

- Link to documentation and small documentation improvements.

### Changed

- Minor server module updates.

## [1.0.0] - 2024-01-03

- Initial repository analysis for FCM + service worker integration.
- Confirmed SW under `/_/theme/` is valid for FCM notifications when bound via `messaging.useServiceWorker(...)`.
- Identified minor bugs and improvement opportunities as listed above.
