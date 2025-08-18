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

### Fixed
- Addressed a lint warning (Ruff F841) in `client_code/messages.py` by avoiding variable shadowing in `BatchResponse.from_fcm_response()`.
- Ensured `BatchResponse.from_fcm_response()` compiles entries from the collected response list consistently (internal cleanup; no external behavior change).

### Notes
- No behavior changes; this release focuses on documentation and maintainability.
- Continues to follow the Unicode Symbol Policy (no Unicode in print statements) and Ruff linting configuration.

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
