from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import List, Optional
import uuid
import time
from brain.auth.role import UserRole

class IntentPriority(IntEnum):
    BACKGROUND = 1
    USER = 10
    EMERGENCY = 100

class IntentScope(Enum):
    RESOURCE = auto()
    TIME = auto()
    ACTION = auto()

@dataclass
class Intent:
    """
    Represents a specific intention from a user (or system) to perform an action 
    that may use resources or conflict with others.
    """
    user_id: str
    role: UserRole
    description: str
    
    intent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: Optional[str] = None
    priority: IntentPriority = IntentPriority.USER
    
    # Conflict Surface
    resources: List[str] = field(default_factory=list) # e.g. ["camera", "arm_left"]
    time_window: Optional[tuple[float, float]] = None # (start, end)
    
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        if not self.time_window:
            return False
        return time.time() > self.time_window[1]

    def overlaps_resource(self, other: 'Intent') -> bool:
        return bool(set(self.resources) & set(other.resources))
