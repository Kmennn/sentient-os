from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import time

class MissionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"
    ESCALATED = "ESCALATED"

@dataclass(frozen=True)
class MissionOutcome:
    """
    Immutable record of a mission's execution result.
    This data is used for cross-mission learning and optimization.
    """
    mission_id: str
    mission_type: str
    status: MissionStatus
    duration: float
    retries: int = 0
    trust_delta: float = 0.0
    failure_reason: Optional[str] = None
    resource_contention: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        # Validate logic if needed, but frozen=True makes it immutable after init.
        pass
