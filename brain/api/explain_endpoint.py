from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType

router = APIRouter()

@router.get("/explain/last")
async def explain_last_decision():
    """
    Returns explanation for the most recent significant autonomous decision.
    """
    try:
        entries = mission_scheduler.autonomy_ledger.get_entries()
        # Filter for relevant decisions (Actions, Suggestions, Rejections)
        relevant_types = {
            DecisionType.ACTION_EXECUTED, 
            DecisionType.SUGGESTED, 
            DecisionType.ACTION_BLOCKED,
            DecisionType.ATTENTION_SUPPRESSED
        }
        
        # Search backwards
        for entry in reversed(entries):
            if entry.decision_type in relevant_types:
                return {
                    "decision_id": entry.decision_id,
                    "type": entry.decision_type.value,
                    "timestamp": entry.timestamp,
                    "reason": entry.reason,
                    "focus_context": entry.focus_state,
                    "explanation": f"I decided to {entry.decision_type.value} because: {entry.reason}"
                }
                
        return {"message": "No recent autonomous decisions to explain."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
