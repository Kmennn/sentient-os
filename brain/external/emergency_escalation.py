import time
from typing import List, Dict, Optional
from brain.external.emergency_ack import EmergencyAck

class EmergencyEscalationManager:
    def __init__(self):
        self._emergencies: Dict[str, EmergencyAck] = {}
        
    def create_emergency(self, signal_id: str, suggestion_id: str) -> EmergencyAck:
        # Check if exists? For now assume new.
        import uuid
        emergency_id = str(uuid.uuid4())
        ack = EmergencyAck(
            emergency_id=emergency_id,
            signal_id=signal_id,
            suggestion_id=suggestion_id,
            created_at=time.time()
        )
        self._emergencies[emergency_id] = ack
        return ack
        
    def get_pending(self) -> List[EmergencyAck]:
        return [e for e in self._emergencies.values() if not e.acknowledged]

    def acknowledge(self, emergency_id: str, user_id: str = "user") -> Optional[EmergencyAck]:
        if emergency_id in self._emergencies:
            ack = self._emergencies[emergency_id]
            if not ack.acknowledged:
                ack.acknowledged = True
                ack.acknowledged_at = time.time()
                ack.acknowledged_by = user_id
                return ack
        return None
        
    def check_escalation(self, now: float = None) -> List[EmergencyAck]:
        """
        Checks for timeouts and increases escalation level.
        Returns list of emergencies that JUST escalated.
        """
        if now is None: now = time.time()
        escalated = []
        
        for ack in self._emergencies.values():
            if ack.acknowledged: continue
            
            elapsed = now - ack.created_at
            new_level = ack.escalation_level
            
            # T+5 min (300s) -> Level 1
            if elapsed > 300 and ack.escalation_level < 1:
                new_level = 1
                
            # T+15 min (900s) -> Level 2
            if elapsed > 900 and ack.escalation_level < 2:
                new_level = 2
                
            if new_level > ack.escalation_level:
                ack.escalation_level = new_level
                escalated.append(ack)
                
        return escalated
        
    def get_highest_level(self) -> int:
        pending = self.get_pending()
        if not pending: return 0
        return max(e.escalation_level for e in pending)
