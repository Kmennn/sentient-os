from fastapi import APIRouter
from dataclasses import asdict
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/autonomy/budget")
def get_autonomy_budget():
    """
    Returns current autonomy budget usage and status.
    """
    trust = mission_scheduler.device_trust_score
    usage = mission_scheduler.budget_manager.get_usage(trust)
    return asdict(usage)
