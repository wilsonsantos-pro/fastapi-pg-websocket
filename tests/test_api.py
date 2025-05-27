# pylint: disable=redefined-outer-name
import json
import threading

import pytest
from sqlalchemy import text

from fastapi_pg_websocket.database import LISTEN_CHANNEL_ORDER


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
