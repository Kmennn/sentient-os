from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import time

@dataclass
class SyncState:
    timestamp: float
    preferences: Dict[str, Any] # Domain -> Level
    meaning_memory: Dict[str, float] # Domain -> Relevance
    trust_score: float
    agent_phase: str
    last_decision_id: Optional[str]
    device_id: str = "unknown"
    
    def to_dict(self):
        return asdict(self)
        
    @staticmethod
    def from_dict(d: Dict[str, Any]):
        return SyncState(**d)
