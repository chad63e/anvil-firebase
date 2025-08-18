"""
Client-side utilities for Anvil Firebase integration.

Provides:
- Environment helpers (debug vs. published) to select the correct app origin.
- Default service worker URL used by the client.
- A small serializer utility for portable classes.
"""

import anvil
import anvil.server


# MARK: Environment helpers

def in_debug():
    """Return True if the app is running in debug mode, otherwise False.

    Uses `anvil.app.environment.tags` to determine whether the current runtime
    includes a "debug" tag.
    """
    environment = anvil.app.environment
    tags = environment.tags or []
    return True if "debug" in tags else False


# MARK: Constants and URLs

# Relative path (under Anvil theme assets) to the service worker file.
SEVICE_WORKER_RELATIVE_PATH = "_/theme/fb-service-worker.js"

# App origin adjusts for debug vs. published.
APP_BASE_URL = (
    anvil.server.get_app_origin()
    if in_debug()
    else anvil.server.get_app_origin("published")
)

# Default URL used for ServiceWorkerContainer.register(...)
DEFAULT_SERVICE_WORKER = f"{APP_BASE_URL}/{SEVICE_WORKER_RELATIVE_PATH}"


# MARK: Data serialization utilities

class DataSerializer:
    """Lightweight attribute-based serializer for portable classes."""

    @staticmethod
    def serialize(cls, attributes: list, ignore_nulls: bool = True):
        """Serialize selected attributes from an object into a dict.

        Args:
            cls: The instance to read attributes from.
            attributes (list): Attribute names to include.
            ignore_nulls (bool): When True, skip attributes whose value is None.

        Returns:
            dict: A dictionary of attribute names to values.
        """
        if ignore_nulls:
            return {
                attr: getattr(cls, attr)
                for attr in attributes
                if getattr(cls, attr) is not None
            }
        else:
            return {attr: getattr(cls, attr) for attr in attributes}
