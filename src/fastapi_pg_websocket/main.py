from fastapi_pg_websocket.logging import config_logging

from .api import app

config_logging()

__all__ = ["app"]
