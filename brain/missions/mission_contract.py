
import uuid
import time
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class AutonomyLevel(Enum):
    ASSIST = "ASSIST"   # Ask before every action
    EXECUTE = "EXECUTE" # Run autonomously until done/error

@dataclass(frozen=True)
class MissionContract:
    """
    Immutable contract defining the scope and boundaries of a mission.
    Once created, it cannot be modified.
    """
    mission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Mission"
    
    # Scope definitions
    allowed_actions: List[str] = field(default_factory=list) # e.g. ['pick', 'place']
    allowed_objects: List[str] = field(default_factory=list) # e.g. ['cup_1', 'box_2']
    
    # Constraints
    max_duration: float = 60.0 # seconds
    autonomy_level: AutonomyLevel = AutonomyLevel.ASSIST
    
    # Metadata
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.max_duration
