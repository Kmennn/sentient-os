from dataclasses import dataclass
from enum import Enum, auto

class DelayTolerance(Enum):
    LOW = auto()    # Hate waiting. Prefer prompt asking or rejecting.
    MEDIUM = auto() # Can wait a bit (e.g. 5-10 mins).
    HIGH = auto()   # Happy to wait (e.g. 30+ mins) to avoid conflict/rejection.

@dataclass
class SchedulingPreferences:
    user_id: str
    delay_tolerance: DelayTolerance = DelayTolerance.MEDIUM
    allow_preemption: bool = False # Allow my low-priority tasks to be preempted by others' equal priority?
