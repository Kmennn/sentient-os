from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class EmergencyAck:
    emergency_id: str
    signal_id: str
    suggestion_id: str
    created_at: float
    acknowledged: bool = False
    acknowledged_at: Optional[float] = None
    acknowledged_by: str = "unknown"
    escalation_level: int = 0
    
    def to_dict(self):
        return {
            "emergency_id": self.emergency_id,
            "signal_id": self.signal_id,
            "suggestion_id": self.suggestion_id,
            "created_at": self.created_at,
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at,
            "acknowledged_by": self.acknowledged_by,
            "escalation_level": self.escalation_level
        }
