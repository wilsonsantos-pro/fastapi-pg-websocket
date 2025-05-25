# pylint: disable=redefined-outer-name
"""The the PGListener.

The tests here try to be as close to a unit test as possible.
For that reason external entities, like a database, are mocked.

Another remark is about asyncio.
The tests here are using pytest-asyncio.
The reason for that is the clients are notified with an async function,
so the current event loop has to be fetched so that the function runs on the correct one.
However, `asyncio.get_event_loop()` since Python 3.12 emits a deprecation warning, so
a loop must pre exist:

    DeprecationWarning: There is no current event loop
"""
import asyncio
import time
from typing import AsyncGenerator
from unittest.mock import Mock

import pytest
import pytest_asyncio
from psycopg2.extensions import connection

import fastapi_pg_websocket.listener
from fastapi_pg_websocket.listener import PGListener
from fastapi_pg_websocket.protocol import Observer

NO_CLIENT_TIMEOUT_SEC = 1


@pytest.fixture(autouse=True)
def no_client_timeout(monkeypatch, request):
    monkeypatch.setattr(
        fastapi_pg_websocket.listener,
        "NO_CLIENT_TIMEOUT_SEC",
        getattr(request, "param", NO_CLIENT_TIMEOUT_SEC),
    )


@pytest.fixture
def conn():
    return Mock(spec=connection)


@pytest.fixture
def client():
    return Mock(spec=Observer)


@pytest_asyncio.fixture(scope="function")
async def listener(monkeypatch, conn) -> AsyncGenerator[PGListener, None]:
    monkeypatch.setattr(fastapi_pg_websocket.listener, "get_raw_db_connection", conn)

    listener = PGListener("some_channel")
    monkeypatch.setattr(listener, "_channel_has_new_data", lambda _: time.sleep(1) or False)

    yield listener

    listener.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("no_client_timeout", [10], indirect=True)
async def test_refresh(listener, client):
    """Client connects and quickly reconnects (refresh)"""
    listener.start()
    assert listener.should_run.is_set()

    listener.add_client(client)
    listener.remove_client(client)
    listener.add_client(client)
    assert listener.should_run.is_set()


@pytest.mark.asyncio
async def test_no_more_clients(listener, client):
    listener.start()
    assert listener.should_run.is_set()

    listener.add_client(client)
    listener.remove_client(client)
    await asyncio.sleep(NO_CLIENT_TIMEOUT_SEC + 1)
    assert not listener.should_run.is_set()
