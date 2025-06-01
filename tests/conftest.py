import os
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from alembic import command
from alembic.config import Config
from fastapi_pg_websocket.app.dependencies import get_db
from fastapi_pg_websocket.database import db_session_ctx
from fastapi_pg_websocket.logging import config_logging

if TYPE_CHECKING:
    from fastapi import FastAPI

    from fastapi_pg_websocket.listener import PGListener


def pytest_configure():
    if os.getenv("LOGGING_ENABLED", False):
        config_logging()


@pytest.fixture
def app() -> "FastAPI":
    from fastapi_pg_websocket.app.api import app as fastapi_app

    return fastapi_app


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    alembic_cfg = Config(os.environ.get("ALEMBIC_CONFIG"))
    command.upgrade(alembic_cfg, "head")


@pytest.fixture()
def db_session():
    with db_session_ctx() as db:
        try:
            yield db
        finally:
            db.rollback()


@pytest.fixture()
def client(app: "FastAPI", db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
        listener: "PGListener | None"
        if listener := getattr(app.state, "listener", None):
            listener.stop()
