
import logging
from typing import List

logger = logging.getLogger(__name__)

class ConfidenceMonitor:
    """
    Monitors runtime confidence of policy execution.
    If variance is high or recent failures occur, signals instability.
    """
    def __init__(self):
        self.variance_threshold = 0.5
        self.history: List[float] = [] # Recent outcome scores or deltas
        
    def record_observation(self, metric: float):
        """
        Record a metric (e.g., predicted blending delta magnitude variance).
        """
        self.history.append(metric)
        if len(self.history) > 10:
            self.history.pop(0)
            
    def is_stable(self) -> bool:
        if len(self.history) < 2:
            return True
        
        # Simple variance check
        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        
        if variance > self.variance_threshold:
            logger.warning(f"Instability Detected: Variance {variance:.2f} > {self.variance_threshold}")
            return False
            
        return True

confidence_monitor = ConfidenceMonitor()
