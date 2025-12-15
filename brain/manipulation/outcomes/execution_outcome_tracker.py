
import logging
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class OutcomeStatus(Enum):
    SUCCESS = "SUCCESS"
    COLLISION = "COLLISION"
    USER_ABORT = "USER_ABORT"
    TIMEOUT = "TIMEOUT"

@dataclass
class ExecutionOutcome:
    timestamp: float
    status: OutcomeStatus
    zone_id: str
    details: str
    duration: float

class ExecutionOutcomeTracker:
    def __init__(self):
        self.history: List[ExecutionOutcome] = []
        
    def record_outcome(self, status: OutcomeStatus, zone_id: str = "default", details: str = "", duration: float = 0.0):
        outcome = ExecutionOutcome(
            timestamp=time.time(),
            status=status,
            zone_id=zone_id,
            details=details,
            duration=duration
        )
        self.history.append(outcome)
        logger.info(f"Outcome Recorded: {status.value} in {zone_id} ({duration:.2f}s)")
        
    def get_zone_stats(self, zone_id: str) -> Dict[str, float]:
        """
        Return failure rate for a zone.
        """
        zone_events = [e for e in self.history if e.zone_id == zone_id]
        if not zone_events:
            return {"failure_rate": 0.0, "total": 0}
            
        failures = [e for e in zone_events if e.status == OutcomeStatus.COLLISION]
        rate = len(failures) / len(zone_events)
        return {"failure_rate": rate, "total": len(zone_events)}

outcome_tracker = ExecutionOutcomeTracker()
