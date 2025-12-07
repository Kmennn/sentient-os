
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import logging

from core.config import config
# from core.llm_service import llm_service (Circular import risk if not careful)

router = APIRouter()
logger = logging.getLogger(__name__)

# Global System Mode
class SystemState:
    AUTONOMY_MODE = "OFF" # OFF, SIMULATED, REAL

system_state = SystemState()

class ActionRequest(BaseModel):
    action: str
    params: Any
    agent_id: str = "user"

class ModeRequest(BaseModel):
    mode: str # OFF, SIMULATED, REAL

@router.post("/v1/system/mode")
async def set_mode(req: ModeRequest):
    allowed = ["OFF", "SIMULATED", "REAL"]
    if req.mode.upper() not in allowed:
        raise HTTPException(status_code=400, detail=f"Mode must be one of {allowed}")
    system_state.AUTONOMY_MODE = req.mode.upper()
    logger.info(f"System Autonomy Mode set to: {system_state.AUTONOMY_MODE}")
    return {"status": "success", "mode": system_state.AUTONOMY_MODE}

@router.get("/v1/system/mode")
async def get_mode():
    return {"mode": system_state.AUTONOMY_MODE}

@router.post("/v1/action/request")
async def request_action(req: ActionRequest):
    """
    Bridge: Receives action request from Agent -> Forwards to Body (if allowed).
    """
    mode = system_state.AUTONOMY_MODE
    logger.info(f"Action Request: {req.action} (Mode: {mode})")

    if mode == "OFF":
        return {"status": "denied", "reason": "Autonomy is OFF"}

    # In SIMULATED or REAL, we proceed to contact Body
    # We add a 'simulation' flag if mode is SIMULATED, 
    # but strictly speaking the Body should also respect the global safety config.
    # Here we trust the Body to handle execution, but we pass the intent.
    
    # Body URL (Local Kernel) - assuming port 8001 based on typical setup
    BODY_URL = "http://localhost:8001/action/run" 
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "action": req.action,
                "params": req.params,
                "mode": mode # Pass the mode to Body
            }
            resp = await client.post(BODY_URL, json=payload, timeout=10.0)
            
            if resp.status_code == 200:
                result = resp.json()
                # Log to DB (TODO: use db.py)
                return {"status": "executed", "result": result}
            else:
                return {"status": "error", "detail": resp.text}
                
    except Exception as e:
        logger.error(f"Bridge connection error: {e}")
        return {"status": "error", "detail": f"Failed to contact Body: {e}"}

@router.post("/v1/agent/run")
async def run_agent_task(query: str):
    """
    Directly trigger the TaskAgent.
    """
    # Import locally to avoid circular import issues
    from core.llm_service import llm_service
    
    # Force TASK intent
    # This is a bit of a hack re-using generate_response logic, 
    # but ideally we'd call agent directly. 
    # For v1.8 MVP, let's just ask LLM service which uses the agent.
    
    response = await llm_service.generate_response(query)
    return {"response": response}
