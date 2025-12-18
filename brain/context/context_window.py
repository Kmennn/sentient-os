from dataclasses import dataclass, field
from typing import Dict, Optional, List
import time
import uuid

@dataclass
class ContextWindow:
    source_device_id: str
    target_device_id: str
    payload: Dict # e.g. {"mission": "Draft Email", "interrupt": "123"}
    window_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    ttl: float = 90.0 # seconds
    
    @property
    def expires_at(self) -> float:
        return self.created_at + self.ttl
        
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
