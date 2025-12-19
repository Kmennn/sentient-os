from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/contextual/search/{signal_id}")
def get_contextual_search(signal_id: str):
    res = mission_scheduler.contextual_search.get_result(signal_id)
    if res:
        return res.to_dict()
    raise HTTPException(status_code=404, detail="Search result not found for this signal")

@router.get("/contextual/narration/{signal_id}")
def get_contextual_narration(signal_id: str):
    res = mission_scheduler.contextual_narrator.get_narration(signal_id)
    if res:
        return res.to_dict()
    raise HTTPException(status_code=404, detail="Narration not found for this signal")

@router.get("/contextual/history/{signal_title}")
def get_contextual_history(signal_title: str):
    # Retrieve recent history from memory
    # Note: Using signal_title instead of ID as per refactor design
    history = mission_scheduler.contextual_memory.get_recent(signal_title, days=30)
    return {"count": len(history), "entries": history}

@router.get("/contextual/patterns/{signal_title}")
def get_contextual_patterns(signal_title: str):
    insight = mission_scheduler.pattern_analyzer.analyze_pattern(signal_title)
    return {
        "count": insight.count,
        "trend": insight.trend,
        "confidence": insight.confidence,
        "last_seen": insight.last_seen
    }

@router.get("/contextual/patterns/{signal_title}/explanation")
def get_pattern_explanation(signal_title: str):
    explanation = mission_scheduler.pattern_narrator.get_explanation(signal_title)
    if explanation:
        return explanation.to_dict()
    raise HTTPException(status_code=404, detail="Explanation not found (or not generated yet)")
