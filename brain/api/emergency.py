from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType

router = APIRouter()

@router.get("/emergency/pending")
def get_pending_emergencies():
    return [e.to_dict() for e in mission_scheduler.emergency_manager.get_pending()]

@router.post("/emergency/{emergency_id}/acknowledge")
def acknowledge_emergency(emergency_id: str):
    ack = mission_scheduler.emergency_manager.acknowledge(emergency_id, "api_user")
    if ack:
        mission_scheduler._log_autonomy_decision(DecisionType.EMERGENCY_ACKNOWLEDGED, suggestion_id=ack.suggestion_id, reason=f"Ack ID: {emergency_id}", was_auto=False)
        return {"status": "acknowledged", "emergency": ack.to_dict()}
    raise HTTPException(status_code=404, detail="Emergency not found or already acknowledged")
