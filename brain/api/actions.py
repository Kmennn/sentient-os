from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.post("/actions/{action_id}/execute")
def execute_action(action_id: str):
    """
    Executes a registered action if safe.
    """
    result = mission_scheduler.action_sandbox.execute_action(action_id, requesting_agent="API_User")
    return result.to_dict()

@router.post("/actions/{action_id}/revert")
def revert_action(action_id: str):
    """
    Reverts a reversible action.
    """
    success = mission_scheduler.action_sandbox.revert_action(action_id)
    if not success:
        raise HTTPException(status_code=400, detail="Action cannot be reverted.")
    return {"status": "reverted", "action_id": action_id}

@router.get("/actions/history")
def get_action_history():
    """
    Returns recent action execution history.
    """
    entries = mission_scheduler.autonomy_ledger.get_entries()
    # Filter for action_executed
    action_events = [e for e in entries if "action" in e.decision_type.value]
    return [e.to_dict() for e in action_events[-20:]] # Last 20
