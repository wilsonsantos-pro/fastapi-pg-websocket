from fastapi_pg_websocket.logging import config_logging

config_logging()

from .api import app  # pylint: disable=wrong-import-position

__all__ = ["app"]
