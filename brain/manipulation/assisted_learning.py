
import logging
from typing import Dict, Optional, List
from brain.manipulation.outcomes.execution_outcome_tracker import outcome_tracker, OutcomeStatus
from brain.memory.physical_memory import physical_memory

logger = logging.getLogger(__name__)

class LearningMonitor:
    """
    Monitors failures and proposes adaptations to the user.
    """
    def __init__(self):
        self.pending_adaptation: Optional[Dict[str, str]] = None
        
    def check_for_adaptations(self, zone_id: str) -> Optional[Dict[str, str]]:
        """
        Called after failure. Returns a proposal if applicable.
        """
        stats = outcome_tracker.get_zone_stats(zone_id)
        rate = stats["failure_rate"]
        
        if rate > 0.2:
            current_clearance = physical_memory.base_clearance
            proposed = physical_memory.get_suggested_clearance(zone_id)
            
            if proposed > current_clearance:
                diff = proposed - current_clearance
                self.pending_adaptation = {
                    "zone_id": zone_id,
                    "reason": f"High failure rate ({rate:.0%})",
                    "action": f"Increase safety clearance by {diff*100:.0f}cm",
                    "value": str(proposed)
                }
                logger.info(f"Generated Adaptation Proposal: {self.pending_adaptation}")
                return self.pending_adaptation
        return None

    def apply_adaptation(self, approved: bool):
        if approved and self.pending_adaptation:
            logger.info("User APPROVED adaptation. (Mock: Persisting to Memory)")
            # In a real system, we'd explicitly save this override to Memory
            # physical_memory.set_override(...)
        else:
            logger.info("User REJECTED adaptation.")
        
        self.pending_adaptation = None

learning_monitor = LearningMonitor()
