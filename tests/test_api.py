# pylint: disable=redefined-outer-name
import json
import threading

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from fastapi_pg_websocket.database import LISTEN_CHANNEL_ORDER
from fastapi_pg_websocket.orm import User


@pytest.fixture
def notifier_thread_ready(db_session) -> threading.Event:
    ready = threading.Event()

    def trigger_change():
        ready.wait(timeout=5)
        db_session.execute(
            text(f"NOTIFY {LISTEN_CHANNEL_ORDER}, :event"),
            {
                "event": json.dumps({"id": 42, "action": "update"}),
            },
        )
        db_session.commit()

    threading.Thread(target=trigger_change).start()
    return ready


def test_users_notify(client, notifier_thread_ready: threading.Event):

    with client.websocket_connect("/ws/users") as ws:
        # Signal the background thread it's safe to send the notification now
        notifier_thread_ready.set()
        data = ws.receive_text()
        assert "42" in data


def test_change_status(client: TestClient, db_session: Session):
    db_session.execute(
        insert(User).values(
            id=1,
            username="johnsnow",
            email="johnsnow@westeros.com",
            status=1,
        )
    )

    res = client.post("users/1", content="666")
    assert res.status_code == 200
    assert res.json()["status"] == 666
