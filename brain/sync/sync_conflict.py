from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import time

class ConflictType(str, Enum):
    PREFERENCE = "preference"
    MEANING = "meaning"
    TRUST = "trust"

class ConflictResolution(str, Enum):
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    MERGED = "merged"
    REJECTED = "rejected" # If invalid

@dataclass
class SyncConflict:
    conflict_id: str
    domain: str
    conflict_type: ConflictType
    local_value: Any
    remote_value: Any
    resolution: ConflictResolution
    resolved_value: Any
    reason: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self):
        return {
            "conflict_id": self.conflict_id,
            "domain": self.domain,
            "conflict_type": self.conflict_type.value,
            "local_value": str(self.local_value),
            "remote_value": str(self.remote_value),
            "resolution": self.resolution.value,
            "resolved_value": str(self.resolved_value),
            "reason": self.reason,
            "timestamp": self.timestamp
        }
