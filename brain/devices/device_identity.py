from enum import StrEnum, auto
from dataclasses import dataclass, field
from typing import List
import time

class DeviceType(StrEnum):
    DESKTOP = auto()
    MOBILE = auto()
    TABLET = auto()
    CLI = auto()

@dataclass
class DeviceIdentity:
    device_id: str
    device_type: DeviceType
    capabilities: List[str] = field(default_factory=list) # e.g. ["TOAST", "PANEL", "AUDIO"]
    last_seen: float = field(default_factory=time.time)
    
    # Trust / Confidence Fields (v10.5.2)
    trust_score: float = 0.5
    last_trust_update: float = field(default_factory=time.time)
    
    @property
    def is_active(self):
        # Active if seen in last 60 seconds
        return (time.time() - self.last_seen) < 60
        
    def get_current_trust(self) -> float:
        """Calculates score based on time elapsed since last update."""
        now = time.time()
        elapsed_mins = (now - self.last_trust_update) / 60.0
        if elapsed_mins <= 0:
            return self.trust_score
            
        decay_rate_per_min = 0.02
        decay = elapsed_mins * decay_rate_per_min
        return max(0.0, self.trust_score - decay)
        
    def boost_trust(self, amount: float = 0.05):
        """Register an interaction => boost score."""
        current = self.get_current_trust()
        self.trust_score = min(1.0, current + amount)
        self.last_trust_update = time.time()

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "device_type": self.device_type.value,
            "capabilities": self.capabilities,
            "last_seen": self.last_seen,
            "trust_score": self.trust_score,
            "last_trust_update": self.last_trust_update
        }
    
    @classmethod
    def from_dict(cls, data):
        data_trust = data.get("trust_score", 0.5)
        # Validate trust range on load (Safety Rule 5)
        if not isinstance(data_trust, (int, float)) or data_trust < 0 or data_trust > 1:
            data_trust = 0.2 # Safe low default if corrupt
            
        return cls(
            device_id=data["device_id"],
            device_type=DeviceType(data["device_type"]),
            capabilities=data.get("capabilities", []),
            last_seen=data.get("last_seen", 0.0),
            trust_score=data_trust,
            last_trust_update=data.get("last_trust_update", time.time())
        )
