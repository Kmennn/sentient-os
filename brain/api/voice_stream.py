import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.llm.llm_service import LLMService
from api.ws_handlers import manager 

router = APIRouter()
logger = logging.getLogger(__name__)

# TODO: Inject a proper STT engine (e.g. wrapper around Vosk or Whisper)
# For v1.10 Phase 3, we might assume the client sends text OR raw audio.
# If raw audio, we need an STT Service.
# For now, let's assume the local kernel might do STT or send audio for server-side STT.
# The user prompt mentions "Brain/voice_stream/ -> WS endpoint for partial transcripts".
# This likely means the Brain does the STT or at least handles the stream.

@router.websocket("/v1/voice/stream")
async def voice_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Voice stream connected")
    try:
        while True:
            # Receive data (could be bytes for audio or text for control)
            data = await websocket.receive()
            
            if "bytes" in data:
                audio_chunk = data["bytes"]
                # Process audio_chunk with STT Engine
                # transcript_partial = stt_engine.process(audio_chunk)
                
                # Mock STT for now to verify pipeline
                transcript_partial = "..." 
                
                # Broadcast for UI
                await manager.broadcast_json({
                    "type": "voice.transcript",
                    "payload": {
                        "text": transcript_partial,
                        "is_final": False
                    }
                })
                pass
            
            if "text" in data:
                # Handle control messages or pre-transcribed text
                msg = json.loads(data["text"])
                logger.info(f"Received control message: {msg}")
                
    except WebSocketDisconnect:
        logger.info("Voice stream disconnected")
    except Exception as e:
        logger.error(f"Voice stream error: {e}")

