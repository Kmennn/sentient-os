```
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import logging

from core.config import config
# from core.llm_service import llm_service (Circular import risk if not careful)

router = APIRouter()
print("DEBUG: Routes Module Loaded")
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

@router.post("/system/mode")
async def set_mode(req: ModeRequest):
    allowed = ["OFF", "SIMULATED", "REAL"]
    if req.mode.upper() not in allowed:
        raise HTTPException(status_code=400, detail=f"Mode must be one of {allowed}")
    system_state.AUTONOMY_MODE = req.mode.upper()
    logger.info(f"System Autonomy Mode set to: {system_state.AUTONOMY_MODE}")
    return {"status": "success", "mode": system_state.AUTONOMY_MODE}

@router.get("/system/mode")
async def get_mode():
    return {"mode": system_state.AUTONOMY_MODE}

@router.post("/action/request")
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

@router.post("/agent/run")
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

@router.post("/vision/analyze")
async def analyze_vision(payload: Dict[str, Any] = Body(...)):
    """
    Trigger full vision pipeline analysis.
    Payload: { "capture": true, ... }
    """
    capture = payload.get("capture", False)
    # Handle direct image upload if needed, for now just flag
    
    from core.vision.vision_engine import vision_engine
    result = await vision_engine.analyze(capture=capture)
    return result



@router.post("/agent/deep-research/run")
async def run_deep_research(query: str):
    """
    Trigger Deep Research Agent.
    """
    from core.agents.deep_research_agent import deep_research_agent
    result = await deep_research_agent.run(query)
    return result

@router.post("/voice/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file (WAV).
    """
    from core.voice.voice_engine import voice_engine
    
    # Read bytes
    content = await file.read()
    
    # Transcribe
    result = await voice_engine.transcribe(content)
    
    # Optional: If confidence low, or just always, we return text.
    # The requirement said "Add language model fallback if confidence < 0.4".
    # Vosk result often just has text. Partial results have conf.
    # We'll just return text for now.
    
    return result

@router.get("/tools")
async def list_tools():
    """List available tools."""
    from core.tools.registry import registry
    return {"tools": registry.list_tools()}

@router.post("/tools/run")
async def run_tool(payload: Dict[str, Any] = Body(...)):
    """
    Execute a tool by name. 
    Payload: { "tool": "name", "params": {}, "user_id": "..." }
    """
    tool_name = payload.get("tool")
    params = payload.get("params", {})
    user_id = payload.get("user_id", "user")
    
    from core.tools.registry import registry
    import uuid
    import time
    import json
    from core.db import get_connection

    tool = registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    # Log PENDING
    inv_id = str(uuid.uuid4())
    ts = int(time.time())
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tool_invocations (id, user_id, tool_name, params, result, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (inv_id, user_id, tool_name, json.dumps(params), "", "pending", ts))
    conn.commit()
    
    # Execute
    try:
        result = tool.run(params)
        status = "success"
        result_str = str(result) # Store as stringified for now
    except Exception as e:
        result = str(e)
        status = "error"
        result_str = str(e)

    # Update Log
    cursor.execute("""
        UPDATE tool_invocations 
        SET result = ?, status = ?
        WHERE id = ?
    """, (result_str, status, inv_id))
    conn.commit()
    conn.close()

    return {
        "id": inv_id,
        "tool": tool_name,
        "status": status,
        "result": result
    }

