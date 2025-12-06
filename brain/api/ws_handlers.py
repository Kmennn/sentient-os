from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
from core.llm_service import llm_service
from core.memory_service import memory_service
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Store active connections. In production, this would be Redis Pub/Sub.
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    session_id = "default" # TODO: Extract from headers or query param
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse message
            try:
                msg_obj = json.loads(data)
                msg_type = msg_obj.get("type", "chat") # Default to legacy chat
                content = msg_obj.get("content") or msg_obj.get("payload", {}).get("text")
                user_id = msg_obj.get("user_id", session_id)
            except:
                msg_type = "chat"
                content = data
                user_id = session_id

            # === New v1.2 Protocol Handlers ===
            if msg_type == "status.ping":
                await manager.send_personal_message(json.dumps({"type": "status.pong"}), websocket)
                continue

            if msg_type == "memory.dump":
                # Debugging tool for the UI
                hist = memory_service.get_full_context(user_id, limit=10)
                await manager.send_personal_message(json.dumps({
                    "type": "memory.dump.result",
                    "payload": hist
                }), websocket)
                continue
            
            # Legacy ping
            if msg_type == "ping":
                await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
                continue

            # Process chat
            history = memory_service.get_history(user_id)
            response_text = await llm_service.generate_response(content, history)
            
            # Store context
            memory_service.add_message(user_id, "user", content)
            memory_service.add_message(user_id, "assistant", response_text)

            # Reply (Legacy)
            if msg_type == "chat":
                reply = {
                    "type": "chat.reply",
                    "content": response_text
                }
                await manager.send_personal_message(json.dumps(reply), websocket)
            
            # Reply (New Spec)
            elif msg_type == "conversation.turn":
                reply = {
                    "type": "conversation.result",
                    "payload": {
                        "text": response_text
                    }
                }
                await manager.send_personal_message(json.dumps(reply), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
