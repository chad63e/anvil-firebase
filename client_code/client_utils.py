import anvil.server
import anvil


def in_debug():
    environment = anvil.app.environment
    tags = environment.tags or []
    return True if "debug" in tags else False


SEVICE_WORKER_RELATIVE_PATH = "_/theme/fb-service-worker.js"
APP_BASE_URL = (
    anvil.server.get_app_origin()
    if in_debug()
    else anvil.server.get_app_origin("published")
)
DEFAULT_SERVICE_WORKER = f"{APP_BASE_URL}/{SEVICE_WORKER_RELATIVE_PATH}"


class DataSerializer:
    @staticmethod
    def serialize(cls, attributes: list, ignore_nulls: bool = True):
        if ignore_nulls:
            return {
                attr: getattr(cls, attr)
                for attr in attributes
                if getattr(cls, attr) is not None
            }
        else:
            return {attr: getattr(cls, attr) for attr in attributes}
