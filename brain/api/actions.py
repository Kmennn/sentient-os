from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.post("/actions/{action_id}/execute")
def execute_action(action_id: str):
    """
    Executes a registered action if safe.
    """
    success = mission_scheduler.action_sandbox.execute_action(action_id, requesting_agent="API_User")
    if not success:
        raise HTTPException(status_code=403, detail="Action blocked by Safe Sandbox or ID unknown.")
    return {"status": "executed", "action_id": action_id}

@router.post("/actions/{action_id}/revert")
def revert_action(action_id: str):
    """
    Reverts a reversible action.
    """
    success = mission_scheduler.action_sandbox.revert_action(action_id)
    if not success:
        raise HTTPException(status_code=400, detail="Action cannot be reverted.")
    return {"status": "reverted", "action_id": action_id}
