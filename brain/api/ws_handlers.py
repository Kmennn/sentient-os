from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
from core.llm.llm_service import LLMService
from core.memory_service import memory_service
from sync.broadcast import broadcast_service as manager
import json

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    session_id = "default" # TODO: Extract from headers or query param
    
    try:
        while True:
            # Keep-alive Ping (Server -> Client) could be implemented here with asyncio.create_task 
            # or rely on client-side pings which we handle below.

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

            # === v1.3 Protocol ===
            if msg_type == "wake.trigger":
                # Log event
                # In real system: verify audio confidence
                await manager.send_personal_message(json.dumps({"type": "wake.ack"}), websocket)
                continue

            if msg_type == "client.pong":
                # Client acknowledging server ping
                continue

            if msg_type == "action.confirm":
                # User confirmed an action via UI
                payload = msg_obj.get("payload", {})
                action_id = payload.get("action_id")
                
                # Notify User of success (before execution)
                await manager.send_personal_message(json.dumps({
                    "type": "notification", 
                    "content": "Action Confirmed. Executing..."
                }), websocket)
                
                # EXECUTE VIA LLM SERVICE STATE
                result = await llm_service.confirm_action(action_id)
                
                await manager.send_personal_message(json.dumps({
                    "type": "notification", 
                    "content": f"Status: {result}"
                }), websocket)
                
                continue

            # === v1.2 Protocol ===
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

            # Safety Check
            from core.safety import safety_layer
            if content and not safety_layer.validate_message(content):
                await manager.send_personal_message(json.dumps({
                    "type": "error", 
                    "content": "Message blocked by safety layer."
                }), websocket)
                continue

            # Process chat
            history = memory_service.get_history(user_id)
            response_text = await llm_service.generate_response(content, history)
            
            # Store context
            memory_service.add_message(user_id, "user", content)
            memory_service.add_message(user_id, "assistant", response_text)
            
            # v1.10: Broadcast Memory Update
            # In a real system, we'd summarize the new state. For now, sending a signal.
            await manager.broadcast_memory_update(f"New interaction from {user_id}")

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
