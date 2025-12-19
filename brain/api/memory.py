from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/memory/meaning")
def get_user_meanings():
    """
    Returns the accumulated user meaning/relevance scores for distinct domains.
    """
    meanings = mission_scheduler.meaning_memory.get_all_meanings()
    return {
        "count": len(meanings),
        "meanings": meanings
    }
