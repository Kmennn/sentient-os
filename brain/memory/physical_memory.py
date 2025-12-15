
import logging
from brain.manipulation.outcomes.execution_outcome_tracker import outcome_tracker, OutcomeStatus

logger = logging.getLogger(__name__)

class PhysicalMemory:
    """
    Non-Verbal Learning from Physical Interactions.
    """
    def __init__(self):
        self.tracker = outcome_tracker
        self.base_clearance = 0.1 # 10cm default

    def get_suggested_clearance(self, zone_id: str) -> float:
        """
        Adapt clearance based on history.
        """
        stats = self.tracker.get_zone_stats(zone_id)
        rate = stats["failure_rate"]
        
        # Simple Logic:
        # If failure rate > 20%, increase clearance by 50%
        # If failure rate > 50%, increase clearance by 100%
        
        if rate > 0.5:
            suggested = self.base_clearance * 2.0
            logger.info(f"Memory: High failure rate ({rate:.2f}) in {zone_id}. Suggesting 2x clearance.")
            return suggested
        elif rate > 0.2:
            suggested = self.base_clearance * 1.5
            logger.info(f"Memory: Moderate failure rate ({rate:.2f}) in {zone_id}. Suggesting 1.5x clearance.")
            return suggested
            
        return self.base_clearance

physical_memory = PhysicalMemory()
