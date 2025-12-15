
import heapq
import time
import logging
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import List, Optional, Any

logger = logging.getLogger(__name__)

class MissionPriority(IntEnum):
    BACKGROUND = 1
    SYSTEM = 5
    USER = 10
    CRITICAL = 20

@dataclass(order=True)
class QueuedMission:
    priority: int
    timestamp: float
    mission_id: str = field(compare=False)
    payload: Any = field(compare=False, default=None)

class MissionScheduler:
    """
    Manages mission execution order based on priority.
    Only allows one Active Mission at a time.
    """
    def __init__(self):
        self._queue: List[QueuedMission] = []
        self._active_mission: Optional[QueuedMission] = None
        
    def schedule(self, mission_id: str, priority: MissionPriority, payload: Any = None):
        # Heapq is min-heap, so negate priority to get Max-Priority behavior
        # But wait, python heapq pops smallest item. If we want highest priority first,
        # we should store inverted priority?
        # Let's say User=10, Background=1. 
        # If we store -10 vs -1, -10 is smaller, so it pops first. Correct.
        entry = QueuedMission(-priority.value, time.time(), mission_id, payload)
        heapq.heappush(self._queue, entry)
        logger.info(f"Scheduled Mission: {mission_id} (Pri: {priority.name})")
        
    def tick(self) -> Optional[str]:
        """
        Decides which mission should run. 
        Returns 'PREEMPT' if current active should stop,
        'START_NEW' if we should pick next from queue,
        or None if no change.
        """
        if not self._queue:
            return None
            
        top_mission = self._queue[0]
        
        # If nothing active, start top
        if not self._active_mission:
            self._start_mission(heapq.heappop(self._queue))
            return "START_NEW"
            
        # If active exists, check if top_mission is higher priority
        # Remember priority is negative. So smaller value = higher priority.
        if top_mission.priority < self._active_mission.priority:
            # Preemption!
            logger.info(f"Preempting {self._active_mission.mission_id} for {top_mission.mission_id}")
            self._preempt_active()
            return "PREEMPT"
            
        return None
        
    def _start_mission(self, mission: QueuedMission):
        self._active_mission = mission
        logger.info(f"Starting Mission: {mission.mission_id}")
        
    def _preempt_active(self):
        if self._active_mission:
            # Return to queue? Or paused list?
            # For this simplified logic, push back to queue but maybe preserve state elsewhere.
            # We push it back.
            heapq.heappush(self._queue, self._active_mission)
            self._active_mission = None
            
    def complete_active(self):
        self._active_mission = None

mission_scheduler = MissionScheduler()
