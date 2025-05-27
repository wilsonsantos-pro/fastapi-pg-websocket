import logging

from fastapi import Depends, FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_pg_websocket.app.dependencies import get_db
from fastapi_pg_websocket.database import LISTEN_CHANNEL_ORDER
from fastapi_pg_websocket.listener import PGListener
from fastapi_pg_websocket.orm import User
from fastapi_pg_websocket.typing import EntityId

app = FastAPI()

logger = logging.getLogger(__name__)


class WebSocketClient:

    def __init__(self, websocket: WebSocket, entity_id: EntityId | None = None) -> None:
        self.websocket = websocket
        self.entity_id = entity_id

    async def send_text(self, data: str) -> None:
        await self.websocket.send_text(data)


@app.websocket("/ws/users")
async def updates_all_user(websocket: WebSocket):
    await websocket.accept()

    if not hasattr(websocket.app.state, "listener") or not websocket.app.state.listener.is_alive():
        websocket.app.state.listener = PGListener(channel=LISTEN_CHANNEL_ORDER)
        websocket.app.state.listener.start()

    client = WebSocketClient(websocket)
    websocket.app.state.listener.add_client(client)

    try:
        while True:
            await websocket.receive_text()
    except:
        websocket.app.state.listener.remove_client(client)


@app.websocket("/ws/users/{user_id}")
async def updates_user(request: WebSocket, user_id: int):
    await request.accept()

    if not hasattr(request.app.state, "listener") or not request.app.state.listener.is_alive():
        request.app.state.listener = PGListener(channel=LISTEN_CHANNEL_ORDER)
        request.app.state.listener.start()

    client = WebSocketClient(request, user_id)
    request.app.state.listener.add_client(client)

    try:
        while True:
            await request.receive_text()
    except:
        request.app.state.listener.remove_client(client)


HTML = """
<!DOCTYPE html>
<html>
<body>
  <h2>WebSocket DB Listener</h2>
  <ul id="messages"></ul>
  <script>
    const ws = new WebSocket("%s");
    ws.onmessage = function(event) {
      const li = document.createElement("li");
      li.textContent = "Update: " + event.data;
      document.getElementById("messages").appendChild(li);
    };
  </script>
</body>
</html>
"""

BASE_URL = "ws://localhost:8000/ws/users"


@app.get("/users/tacking")
async def users_tracking():
    return HTMLResponse(HTML % BASE_URL)


@app.get("/users/{user_id}/tracking")
async def user_id_tracking(user_id: int):
    return HTMLResponse(HTML % f"{BASE_URL}/{user_id}")


@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.scalars(select(User)).all()
