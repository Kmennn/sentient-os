from fastapi import APIRouter, Body
from dataclasses import asdict
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.override_token import OverrideScope
import time

router = APIRouter()

@router.post("/autonomy/override")
def request_override(
    scope: str = Body(..., embed=True),
    reason: str = Body(..., embed=True)
):
    """
    Request a manual override of safety systems.
    """
    try:
        scope_enum = OverrideScope(scope)
    except ValueError:
        return {"error": "Invalid scope. Use ACTION, RECOVERY, BUDGET, or ALL"}
        
    token = mission_scheduler.override_manager.request_override(scope_enum, reason)
    return asdict(token)

@router.get("/autonomy/override/active")
def get_active_override():
    """
    Returns active override token info.
    """
    token = mission_scheduler.override_manager.get_active_token()
    if token:
        return {
            "active": True,
            "scope": token.scope.value,
            "remaining_seconds": max(0, token.expires_at - time.time()),
            "reason": token.reason
        }
    return {"active": False}
