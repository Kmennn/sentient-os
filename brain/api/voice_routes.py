
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.voice.continuous_engine import continuous_engine
from core.agents.persistence import persistence_service
import logging

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger("voice_api")

@router.websocket("/stream")
async def websocket_voice_stream(websocket: WebSocket):
    await websocket.accept()
    session = continuous_engine.create_session()
    logger.info("Voice stream connected.")
    
    try:
        while True:
            data = await websocket.receive_bytes()
            # Process
            result = session.process_chunk(data)
            
            # Send back if there's text (partial or final)
            if "error" in result:
                await websocket.send_json(result)
                break
                
            text = result.get("text", "")
            is_final = result.get("final", False)
            
            if text or is_final:
                await websocket.send_json({
                    "type": "transcription",
                    "text": text,
                    "is_final": is_final
                })
                
                # If final, maybe persist or intent detection?
                # User wants "Continuous STT", intent detection is separate step usually.
                # But for now, we just stream text back.
                
    except WebSocketDisconnect:
        logger.info("Voice stream disconnected.")
    except Exception as e:
        logger.error(f"Voice stream error: {e}")
        try:
            await websocket.close()
        except:
            pass
