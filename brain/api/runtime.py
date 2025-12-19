from fastapi import APIRouter
from dataclasses import asdict
from brain.missions.mission_scheduler import mission_scheduler
from brain.runtime.execution_state import ActionPhase

router = APIRouter()

@router.get("/runtime/state")
def get_runtime_state():
    """Returns current execution state."""
    state = mission_scheduler.execution_store.get_state()
    return asdict(state)

@router.post("/runtime/recover/{action_id}")
def recover_action(action_id: str):
    """
    Acknowledges interruption and attempts retry.
    Note: Real retry logic would reinvoke the action. 
    Here we clear the state to allow new actions.
    """
    state = mission_scheduler.execution_store.get_state()
    if state.active_action_id == action_id and state.action_phase == ActionPhase.INTERRUPTED:
        # Clear state to unblock
        mission_scheduler.execution_store.clear_state()
        return {"status": "recovered", "message": "State cleared. You may retry manually."}
    return {"error": "Action not in interrupted state"}

@router.post("/runtime/abort/{action_id}")
def abort_action(action_id: str):
    """
    Acknowledges interruption and aborts.
    """
    state = mission_scheduler.execution_store.get_state()
    if state.active_action_id == action_id and state.action_phase == ActionPhase.INTERRUPTED:
        mission_scheduler.execution_store.clear_state()
        return {"status": "aborted", "message": "State cleared."}
    return {"error": "Action not in interrupted state"}
