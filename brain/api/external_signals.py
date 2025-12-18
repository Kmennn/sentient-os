from fastapi import APIRouter
from typing import List
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/external/signals", response_model=List[dict])
async def get_external_signals():
    """Returns recent external signals."""
    try:
        signals = mission_scheduler.external_observer.get_recent_signals(limit=50)
        return [s.to_dict() for s in signals]
    except Exception as e:
        print(f"[API] Error fetching external signals: {e}")
        return []
