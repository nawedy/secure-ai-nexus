from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
from ...security import auth
from ...models import schemas
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.system_stats = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "active_users": 0
        }

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        await self.broadcast_stats()

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast_stats(self):
        """Broadcast system stats to all connected clients"""
        if not self.active_connections:
            return

        self.system_stats["active_users"] = len(self.active_connections)

        for connection in self.active_connections.values():
            try:
                await connection.send_json(self.system_stats)
            except:
                continue

    async def start_periodic_updates(self):
        """Start periodic system stats updates"""
        while True:
            await self.update_system_stats()
            await self.broadcast_stats()
            await asyncio.sleep(5)  # Update every 5 seconds

    async def update_system_stats(self):
        """Update system statistics"""
        # Add your system monitoring logic here
        pass

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    current_user: schemas.User = Depends(auth.get_current_user)
):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process received data if needed
            await manager.broadcast_stats()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast_stats()
