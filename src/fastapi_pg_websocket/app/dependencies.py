from logging import getLogger
from typing import AsyncGenerator

from sqlalchemy.orm import Session

from fastapi_pg_websocket.database import db_session_ctx

logger = getLogger(__name__)


async def get_db() -> AsyncGenerator[Session, None]:
    with db_session_ctx() as db:
        yield db
