from typing import List
import logging

from fastapi.websockets import WebSocket

logger = logging.getLogger(__name__)


class WSConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        logger.info(f"Broadcasting to {len(self.active_connections)} clients-")
        for connection in self.active_connections:
            await connection.send_text(message)
