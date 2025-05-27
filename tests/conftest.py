import os
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from fastapi_pg_websocket.database import SessionLocal, db_session_ctx
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


# from myapp.main import app  # , get_db


# from myapp.db import Base  # Your SQLAlchemy base

# Use a real PostgreSQL test database
# TEST_DATABASE_URL = "postgresql+psycopg2://test_user:test_pass@localhost:5433/test_db"

# Engine and session for tests
# engine = create_engine(TEST_DATABASE_URL)
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @pytest.fixture(scope="session", autouse=True)
# def setup_test_db():
#     Base.metadata.create_all(bind=engine)
#     yield
#     Base.metadata.drop_all(bind=engine)


# Dependency override
@pytest.fixture()
def db_session():
    with db_session_ctx() as db:
        try:
            yield db
        finally:
            db.rollback()


@pytest.fixture()
# def client(db_session):
def client(app: "FastAPI"):
    # app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
        listener: "PGListener | None"
        if listener := getattr(app.state, "listener", None):
            listener.stop()
