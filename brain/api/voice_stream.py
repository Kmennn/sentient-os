from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/v1/voice/stream")
async def voice_stream_endpoint(websocket: WebSocket):
    pass
