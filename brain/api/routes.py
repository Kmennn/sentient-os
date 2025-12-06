from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from core.llm_service import llm_service
from core.memory_service import memory_service

router = APIRouter()

class ChatMessage(BaseModel):
    user_id: str
    message: str

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/chat")
async def chat(msg: ChatMessage):
    # Get history
    history = memory_service.get_history(msg.user_id)
    
    # Generate response
    response_text = await llm_service.generate_response(msg.message, history)
    
    # Store interaction
    memory_service.add_message(msg.user_id, "user", msg.message)
    memory_service.add_message(msg.user_id, "assistant", response_text)
    
    return {"reply": response_text}

@router.get("/memory")
async def get_memory(user_id: str = Query(..., description="User ID"), limit: int = 20):
    return {
        "user_id": user_id,
        "history": memory_service.get_full_context(user_id, limit)
    }
