# pylint: disable=bare-except
import asyncio
import json
import logging
import select
import threading
from typing import TYPE_CHECKING

from .database import get_raw_db_connection
from .protocol import Observer

if TYPE_CHECKING:
    from psycopg2.extensions import connection

logger = logging.getLogger(__name__)


class PGListener:
    def __init__(self, channel: str):
        self.channel = channel
        self.thread: threading.Thread | None = None
        self.should_run: threading.Event = threading.Event()
        self.lock: threading.Lock = threading.Lock()
        self.clients: set[Observer] = set()
        self.loop = asyncio.get_event_loop()

    def start(self):
        with self.lock:
            if not self.thread or not self.thread.is_alive():
                self.should_run.set()
                self.thread = threading.Thread(target=self._listen, daemon=True)
                self.thread.start()

    def is_alive(self) -> bool:
        return self.thread is not None and self.thread.is_alive()

    def add_client(self, client: Observer) -> None:
        self.clients.add(client)

    def remove_client(self, client: Observer) -> None:
        self.clients.discard(client)
        if not self.clients:
            self.should_run.clear()

    def _listen(self):
        conn = get_raw_db_connection()
        try:
            self._listen_to_channel(conn)
        finally:
            conn.close()
            logger.info("Listener stopped [channel=%s]", self.channel)

    def _listen_to_channel(self, conn: "connection") -> None:
        cur = conn.cursor()
        cur.execute(f"LISTEN {self.channel};")
        logger.info("Started listening [channel=%s]", self.channel)

        idle_seconds = 0
        while self.should_run.is_set():
            if not self.clients:
                idle_seconds += 1
                if idle_seconds > 30:
                    logger.warning("No clients connected. Stopping listener.")
                    break
            else:
                idle_seconds = 0

            if select.select([conn], [], [], 1) == ([], [], []):
                continue
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                data = json.loads(notify.payload)
                logger.info("Row updated: [id=%d]", data["id"])
                # asyncio.run(notify_clients(self.clients, notify.payload))
                self.loop.call_soon_threadsafe(
                    asyncio.create_task, notify_clients(self.clients.copy(), notify.payload)
                )


async def notify_clients(clients: set[Observer], message: str):
    to_remove = set()
    for client in clients:
        data = json.loads(message)
        client_user_id = client.entity_id
        if client_user_id and client_user_id != data["id"]:
            continue
        try:
            await client.send_text(message)
        except:
            to_remove.add(client)
    clients.difference_update(to_remove)
