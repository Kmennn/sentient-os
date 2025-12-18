from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from brain.autonomy.autonomy_ledger import AutonomyDecision, DecisionType
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/autonomy/history", response_model=List[dict])
async def get_autonomy_history(
    limit: int = Query(50, ge=1, le=500),
    decision_type: Optional[str] = None,
    since_timestamp: Optional[float] = None
):
    try:
        entries = mission_scheduler.autonomy_ledger.get_entries()
        
        # Sort desc (Newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        filtered = []
        for e in entries:
            if decision_type and e.decision_type.value != decision_type:
                continue
            if since_timestamp and e.timestamp < since_timestamp:
                continue
            filtered.append(e.to_dict())
            
            if len(filtered) >= limit:
                break
                
        return filtered
    except Exception as e:
        # Log error, return empty valid list
        print(f"[API] Error fetching autonomy history: {e}")
        return []
