
import logging
import time
from typing import Callable
from brain.learning.confidence_monitor import ConfidenceMonitor, confidence_monitor

logger = logging.getLogger(__name__)

class ExecutionSupervisor:
    """
    Real-time safety watchdog. 
    Monitors execution frequency, stability, and speed.
    """
    def __init__(self, monitor: ConfidenceMonitor = confidence_monitor):
        self.monitor = monitor
        self.max_speed = 2.0
        self.last_check = 0.0
        
    def supervise(self, current_speed: float) -> bool:
        """
        Returns False if execution should ABORT.
        """
        # 1. Check Monitor Stability
        if not self.monitor.is_stable():
            logger.error("Supervisor: Confidence Monitor unstable. ABORTING.")
            return False
            
        # 2. Check Speed Limit
        if current_speed > self.max_speed:
            logger.error(f"Supervisor: Speed Violation ({current_speed} > {self.max_speed}). ABORTING.")
            return False
            
        return True

execution_supervisor = ExecutionSupervisor()
