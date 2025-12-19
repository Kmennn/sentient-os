from fastapi import APIRouter
from brain.missions.mission_scheduler import mission_scheduler
from typing import List

router = APIRouter()

@router.get("/timeline")
def get_timeline(since_seconds: int = 86400):
    """
    Returns a chronological timeline of cognitive events.
    """
    events = mission_scheduler.timeline_builder.build_timeline(duration_seconds=since_seconds)
    return [e.to_dict() for e in events]
