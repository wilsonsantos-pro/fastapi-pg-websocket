import asyncio
import os

import pytest
from fastapi.testclient import TestClient

from fastapi_pg_websocket.api import app
from fastapi_pg_websocket.database import SessionLocal


def pytest_configure():
    logging_enabled = os.getenv("LOGGING_ENABLED", False)
    if logging_enabled:
        _config_logging_test()


def _config_logging_test():
    import logging.config

    import yaml

    config_path = os.getenv("TEST_LOG_CONFIG", "logging.test.yml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
    logging.getLogger(__name__).info("Loaded test logging from %s", config_path)


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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
# def client(db_session):
def client():
    # app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
