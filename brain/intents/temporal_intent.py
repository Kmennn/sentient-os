from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
import time
from brain.intents.intent import Intent

class TimeFlexibility(Enum):
    STRICT = auto()     # Must run in window or expire
    FLEXIBLE = auto()   # Can be delayed significantly
    BACKGROUND_OK = auto() # Can run whenever resources free

@dataclass
class TemporalIntent(Intent):
    """
    Intent with explicit time constraints.
    """
    earliest_start: float = field(default_factory=time.time)
    latest_start: Optional[float] = None # If None, indefinitely valid (until expired by other means)
    expiry: Optional[float] = None # When this intent becomes invalid
    flexibility: TimeFlexibility = TimeFlexibility.FLEXIBLE
    
    def is_expired(self) -> bool:
        if self.expiry and time.time() > self.expiry:
            return True
        if self.latest_start and time.time() > self.latest_start:
            return True
        # Base check using time_window if present (from parent)
        return super().is_expired()

    def can_start_now(self) -> bool:
        return time.time() >= self.earliest_start
