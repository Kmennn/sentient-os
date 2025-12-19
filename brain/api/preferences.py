from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from brain.missions.mission_scheduler import mission_scheduler
from brain.preferences.explicit_preference import ImportanceLevel
from brain.autonomy.autonomy_ledger import DecisionType

router = APIRouter()

class PreferenceSetRequest(BaseModel):
    domain: str
    importance_level: str # low, medium, high, critical

@router.post("/preferences/domain")
def set_preference(req: PreferenceSetRequest):
    try:
        level = ImportanceLevel(req.importance_level.lower())
        pref = mission_scheduler.preference_store.set_preference(req.domain, level)
        
        mission_scheduler._log_autonomy_decision(
            DecisionType.EXPLICIT_PREFERENCE_SET, 
            reason=f"Domain: {req.domain} -> {level.value}", 
            was_auto=False
        )
        
        return {"status": "updated", "preference": pref.to_dict()}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid importance level")

@router.get("/preferences/{domain}")
def get_preference(domain: str):
    effective = mission_scheduler.preference_store.get_effective_preference(domain)
    explicit = mission_scheduler.preference_store.get_explicit_preference(domain)
    
    return {
        "domain": domain,
        "effective": effective,
        "explicit": explicit.to_dict() if explicit else None
    }
