from typing import Protocol

from fastapi_pg_websocket.typing import EntityId


class Observer(Protocol):

    entity_id: EntityId | None

    async def send_text(self, data: str) -> None: ...
