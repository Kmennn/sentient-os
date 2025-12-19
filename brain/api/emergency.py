from fastapi import APIRouter, HTTPException
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType

router = APIRouter()

@router.get("/emergency/pending")
def get_pending_emergencies():
    return [e.to_dict() for e in mission_scheduler.emergency_manager.get_pending()]

@router.post("/emergency/{emergency_id}/acknowledge")
def acknowledge_emergency(emergency_id: str):
    success = mission_scheduler.emergency_manager.acknowledge_emergency(emergency_id, "user_api")
    if success:
        # v14.2 Record Meaning (High positive for Ack)
        # We need the signal domain.
        # Ideally EmergencyManager returns the ack entry which has it, or we look it up.
        # For now, let's assume EmergencyManager can provide the signal, or we retrieve it.
        # Actually ack_entry has .signal_id?
        # Let's peek into ack dictionary if possible or just assume "SECURITY" if implicit?
        # Better: get the domain from the signal associated with this emergency.
        
        # Accessing private _emergencies for quick lookup (pragmatic)
        ack_entry = mission_scheduler.emergency_manager._emergencies.get(emergency_id)
        domain = "unknown"
        if ack_entry:
           # We need to find the signal.
           # EmergencyAck doesn't store domain directly, but signal_id.
           # Searching external observer history?
           # Or just passed in via metadata.
           # Let's use a safe default or lookup if easy.
           # Lookup:
           for sig in mission_scheduler.external_observer._signals:
               if sig.signal_id == ack_entry.signal_id:
                   domain = sig.domain.value
                   break
        
        mission_scheduler.record_meaning_interaction(domain, InteractionType.ACK, source_id=emergency_id)
        
        return {"status": "acknowledged", "id": emergency_id}
    raise HTTPException(status_code=404, detail="Emergency not found or already acknowledged")
