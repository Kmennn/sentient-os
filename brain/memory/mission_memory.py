from typing import List, Dict, Optional
import logging
from brain.missions.mission_outcome import MissionOutcome, MissionStatus

logger = logging.getLogger(__name__)

class MissionMemory:
    """
    In-memory store for historical mission outcomes.
    Designed for fast lookups by mission type to support optimization and trust scaling.
    """
    def __init__(self):
        # Index by mission_type -> List[MissionOutcome]
        self._outcomes_by_type: Dict[str, List[MissionOutcome]] = {}
        # Simple list for all outcomes
        self._all_outcomes: List[MissionOutcome] = []

    def add_outcome(self, outcome: MissionOutcome):
        """
        Record a new mission outcome.
        """
        if outcome.mission_type not in self._outcomes_by_type:
            self._outcomes_by_type[outcome.mission_type] = []
        
        self._outcomes_by_type[outcome.mission_type].append(outcome)
        self._all_outcomes.append(outcome)
        logger.debug(f"Recorded outcome for {outcome.mission_type}: {outcome.status.name}")

    def get_outcomes(self, mission_type: str, limit: int = 10) -> List[MissionOutcome]:
        """
        Retrieve most recent outcomes for a specific mission type.
        """
        if mission_type not in self._outcomes_by_type:
            return []
        
        # Return last `limit` items, reversed (newest first)
        return self._outcomes_by_type[mission_type][-limit:][::-1]

    def get_stats(self, mission_type: str) -> Dict[str, float]:
        """
        Calculate aggregate statistics for a mission type.
        """
        outcomes = self.get_outcomes(mission_type, limit=50) # Look at last 50 for stats
        if not outcomes:
            return {
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "sample_size": 0
            }

        success_count = sum(1 for o in outcomes if o.status == MissionStatus.SUCCESS)
        total_duration = sum(o.duration for o in outcomes)
        
        return {
            "success_rate": success_count / len(outcomes),
            "avg_duration": total_duration / len(outcomes),
            "sample_size": len(outcomes)
        }

mission_memory = MissionMemory()
