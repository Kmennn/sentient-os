
from fastapi import WebSocket
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class SyncBroadcastService:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_raw(self, message: str):
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast raw: {e}")
                self.disconnect(connection)

    async def broadcast_json(self, data: Dict[str, Any]):
        await self.broadcast_raw(json.dumps(data))

    async def broadcast(self, event_type: str, payload: Dict[str, Any]):
        """
        Broadcasts a structured event to all connected clients.
        """
        message = {
            "type": event_type,
            "payload": payload
        }
        json_msg = json.dumps(message)
        
        # Iterate over copy to safely handle disconnects during iteration
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(json_msg)
            except Exception as e:
                logger.warning(f"Failed to broadcast to client: {e}")
                self.disconnect(connection)

    async def broadcast_agent_event(self, agent_name: str, status: str, details: str = ""):
        await self.broadcast("agent:event", {
            "agent": agent_name,
            "status": status,
            "details": details
        })

    async def broadcast_task_update(self, task_id: str, status: str, percentage: int):
        await self.broadcast("task:update", {
            "task_id": task_id,
            "status": status,
            "percentage": percentage
        })

    async def broadcast_memory_update(self, context_summary: str):
        await self.broadcast("memory:update", {
            "summary": context_summary
        })

    async def broadcast_diagnostics(self, stats: Dict[str, Any]):
        await self.broadcast("diagnostic:panel", stats)

# Global Instance
broadcast_service = SyncBroadcastService()
