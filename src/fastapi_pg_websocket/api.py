import logging

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from .database import LISTEN_CHANNEL_ORDER
from .listener import PGListener
from .typing import EntityId

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

    if not hasattr(app.state, "listener") or not app.state.listener.is_alive():
        app.state.listener = PGListener(channel=LISTEN_CHANNEL_ORDER)
        app.state.listener.start()

    client = WebSocketClient(websocket)
    app.state.listener.add_client(client)

    try:
        while True:
            await websocket.receive_text()
    except:
        app.state.listener.remove_client(client)


@app.websocket("/ws/users/{user_id}")
async def updates_user(websocket: WebSocket, user_id: int):
    await websocket.accept()

    if not hasattr(app.state, "listener") or not app.state.listener.is_alive():
        app.state.listener = PGListener(LISTEN_CHANNEL_ORDER)
        app.state.listener.start()

    client = WebSocketClient(websocket, user_id)
    app.state.listener.add_client(client)

    try:
        while True:
            await websocket.receive_text()
    except:
        app.state.listener.remove_client(client)


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


@app.get("/users")
async def get():
    return HTMLResponse(HTML % BASE_URL)


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return HTMLResponse(HTML % f"{BASE_URL}/{user_id}")
