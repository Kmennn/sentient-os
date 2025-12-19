from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler

router = APIRouter()

@router.get("/reflection/adjustments")
def get_adjustments():
    """
    Returns pending and recent adjustment proposals.
    """
    engine = mission_scheduler.adjustment_engine
    return {
        "active_proposals": [p.to_dict() for p in engine.active_proposals.values()]
    }

@router.post("/reflection/adjustments/{proposal_id}/approve")
def approve_adjustment(proposal_id: str):
    engine = mission_scheduler.adjustment_engine
    if proposal_id not in engine.active_proposals:
        raise HTTPException(status_code=404, detail="Proposal not found")
        
    engine.approve_proposal(proposal_id)
    return {"status": "approved", "proposal_id": proposal_id}

@router.post("/reflection/adjustments/{proposal_id}/reject")
def reject_adjustment(proposal_id: str):
    engine = mission_scheduler.adjustment_engine
    if proposal_id not in engine.active_proposals:
        raise HTTPException(status_code=404, detail="Proposal not found")
        
    engine.reject_proposal(proposal_id)
    return {"status": "rejected", "proposal_id": proposal_id}
