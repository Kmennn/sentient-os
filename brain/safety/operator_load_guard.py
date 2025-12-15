
import logging
import time
from typing import List

logger = logging.getLogger(__name__)

class OperatorLoadGuard:
    """
    Prevents operator confusion by detecting rapid system mode switching (flickering).
    If system switches between Hybrid and Planner modes too often, lock to Planner-Only.
    """
    def __init__(self):
        self._switch_timestamps: List[float] = []
        self._window_seconds = 10.0
        self._max_switches = 3 # More than 3 switches in 10s = Flicker
        self._locked = False
        
    def record_switch(self):
        """
        Call whenever system falls back or re-engages policy.
        """
        now = time.time()
        self._switch_timestamps.append(now)
        self._cleanup(now)
        
        if len(self._switch_timestamps) > self._max_switches:
            self._locked = True
            logger.warning("Operator Load Guard: FLICKER DETECTED. Locking to Planner Mode.")
            
    def _cleanup(self, now: float):
        self._switch_timestamps = [t for t in self._switch_timestamps if now - t <= self._window_seconds]
        
    def is_locked(self) -> bool:
        return self._locked
        
    def reset(self):
        self._locked = False
        self._switch_timestamps = []

operator_load_guard = OperatorLoadGuard()
