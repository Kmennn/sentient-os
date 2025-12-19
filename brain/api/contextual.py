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
        # v14.2 Record Meaning (View)
        # Need domain. PatternInsight/Narrator doesn't explicitly store domain in the look-up map (keyed by title).
        # But we can try to find it.
        # Or Just use "contextual" if unknown?
        # UserMeaning expects a domain string.
        # PatternExplanation doesn't have domain.
        # Let's try to lookup via memory store recent item?
        # Or pass domain in "explain" and store it in PatternExplanation?
        # Ideally PatternNarrator stores it.
        # Let's assume we can find it or default.
        domain = "unknown"
        # Lookup logic:
        # check memory for this title
        mem = mission_scheduler.contextual_memory.get_recent(signal_title, days=1)
        if mem:
             domain = mem[0].get("domain", "unknown")
             
        mission_scheduler.record_meaning_interaction(domain, InteractionType.VIEW, source_id=signal_title)
        
        return explanation.to_dict()
    raise HTTPException(status_code=404, detail="Explanation not found (or not generated yet)")
