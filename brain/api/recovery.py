from fastapi import APIRouter
from dataclasses import asdict
from brain.missions.mission_scheduler import mission_scheduler
import time

router = APIRouter()

@router.get("/autonomy/recovery")
def get_recovery_status():
    """
    Returns current recovery state.
    """
    # Trigger update
    mission_scheduler.recovery_manager.update()
    
    state = mission_scheduler.recovery_manager.state
    remaining = max(0, state.cooldown_until - time.time())
    
    return {
        "level": state.level.value,
        "triggered_by": state.triggered_by.value if state.triggered_by else None,
        "cooldown_remaining_seconds": remaining,
        "is_action_blocked": mission_scheduler.recovery_manager.is_action_blocked()
    }
