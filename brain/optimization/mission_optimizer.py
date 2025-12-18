from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import logging
from brain.memory.mission_memory import MissionMemory
from brain.missions.mission_outcome import MissionStatus

logger = logging.getLogger(__name__)

class OptimizationAction(Enum):
    SCHEDULE_DELAY = "SCHEDULE_DELAY"
    AVOID_CONCURRENCY = "AVOID_CONCURRENCY"
    TIMEOUT_ADJUSTMENT = "TIMEOUT_ADJUSTMENT"

@dataclass
class OptimizationHint:
    action: OptimizationAction
    target_mission_type: str
    reason: str
    parameter: Optional[float] = None # e.g., delay seconds or timeout multiplier
    related_resource: Optional[str] = None

class MissionOptimizer:
    """
    Analyzes mission history to suggest advisory optimizations.
    """
    def __init__(self, memory: MissionMemory):
        self.memory = memory

    def analyze_history(self, mission_type: str) -> List[OptimizationHint]:
        hints = []
        outcomes = self.memory.get_outcomes(mission_type, limit=10)
        
        if not outcomes:
            return hints

        # Check for repeated failures due to contention
        failures = [o for o in outcomes if o.status in (MissionStatus.FAILURE, MissionStatus.ABORTED)]
        recent_consecutive_failures = 0
        for o in outcomes: # Outcomes are newest first
            if o.status in (MissionStatus.FAILURE, MissionStatus.ABORTED):
                recent_consecutive_failures += 1
            else:
                break
        
        if recent_consecutive_failures >= 2:
            # Check if contention was a common factor
            contention_counts = {}
            for f in failures:
                for r in f.resource_contention:
                    contention_counts[r] = contention_counts.get(r, 0) + 1
            
            # If a specific resource is contended in > 50% of failures
            for resource, count in contention_counts.items():
                if count >= len(failures) / 2:
                    hints.append(OptimizationHint(
                        action=OptimizationAction.AVOID_CONCURRENCY,
                        target_mission_type=mission_type,
                        reason=f"High contention on {resource}",
                        related_resource=resource
                    ))
            
            # Suggest a delay to let system settle
            hints.append(OptimizationHint(
                action=OptimizationAction.SCHEDULE_DELAY,
                target_mission_type=mission_type,
                reason="Multiple consecutive failures",
                parameter=5.0 * recent_consecutive_failures # Backoff
            ))

        return hints

mission_optimizer = None # Will be initialized with global memory
