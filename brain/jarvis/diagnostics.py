
from fastapi import APIRouter, Body
from typing import Dict, Any
from sync.broadcast import broadcast_service
import logging

router = APIRouter(prefix="/jarvis", tags=["jarvis"])
logger = logging.getLogger(__name__)

@router.post("/diagnostics")
async def receive_diagnostics(stats: Dict[str, Any] = Body(...)):
    """
    Receives system diagnostics from Local Kernel (or other sources)
    and broadcasts them to the JARVIS panel via WebSocket.
    """
    # Validate or process stats if needed
    # Broadcast to all connected clients listening for "diagnostic:panel"
    await broadcast_service.broadcast("diagnostic:panel", stats)
    return {"status": "ok"}
