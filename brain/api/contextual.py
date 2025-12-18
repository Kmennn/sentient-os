from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/contextual/search/{signal_id}")
def get_contextual_search(signal_id: str):
    res = mission_scheduler.contextual_search.get_result(signal_id)
    if res:
        return res.to_dict()
    raise HTTPException(status_code=404, detail="Search result not found for this signal")
