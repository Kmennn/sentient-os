from fastapi import APIRouter
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/system/confidence")
def get_system_confidence():
    """
    Returns the current system assurance/confidence level.
    """
    conf = mission_scheduler.get_system_confidence()
    if conf:
        return conf.to_dict()
    return {}
