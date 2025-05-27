import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from psycopg2.extensions import connection

LISTEN_CHANNEL_ORDER = "status_channel"


def get_connection_url(raw: bool = False) -> str:
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT", "5432")
    if raw:
        return f"dbname={db_name} user={db_user} password={db_pass} host={db_host}"

    return f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


def get_raw_db_connection() -> "connection":
    conn = psycopg2.connect(get_connection_url(raw=True))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


engine = create_engine(get_connection_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


@contextmanager
def db_session_ctx() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
