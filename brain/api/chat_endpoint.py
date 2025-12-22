from fastapi import APIRouter, Query
from pydantic import BaseModel
from core.llm_service import llm_service
import logging

router = APIRouter()
logger = logging.getLogger("ChatEndpoint")

class ChatMessage(BaseModel):
    message: str

@router.get("/reply")
async def reply(text: str = Query(..., description="user text")):
    text = text.strip()
    if not text:
        return {"reply": "(empty)"}

    try:
        response = await llm_service.generate_response(text)
        return {"reply": response}
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        return {"reply": f"(error using local model) {e}"}

@router.post("/chat")
async def chat(msg: ChatMessage):
    return await reply(text=msg.message)
