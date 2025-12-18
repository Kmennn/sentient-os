import time
import uuid
from typing import List, Optional, Any

# We can't type hint MissionScheduler easily due to circular deps if we aren't careful.
# using Any for scheduler for now or strict typing with TYPE_CHECKING
from brain.ambient.ambient_insight import AmbientInsight, InsightType

class AmbientObserver:
    """
    Passively observes the system state and generates internal insights.
    Does NOT take action.
    """
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.insights: List[AmbientInsight] = []
        self._last_check = 0
        self._check_interval = 5.0 # Seconds between checks to avoid spamming
        
    def tick(self):
        now = time.time()
        if now - self._last_check < self._check_interval:
            return
            
        self._last_check = now
        self._observe_schedule_pressure()
        self._observe_idle_high_trust()
        
    def _observe_schedule_pressure(self):
        # Look for high queue depth
        # Accessing private _queue is naughty but we are part of the brain.
        queue_depth = len(self.scheduler._queue)
        if queue_depth >= 5:
            # Check if we already have a recent pressure insight
            if self._has_recent_insight(InsightType.SCHEDULE_PRESSURE, 60):
                return
                
            insight = AmbientInsight(
                id=str(uuid.uuid4()),
                type=InsightType.SCHEDULE_PRESSURE,
                description=f"High schedule pressure detected ({queue_depth} missions queued).",
                confidence=0.8
            )
            self._log_insight(insight)
            
    def _observe_idle_high_trust(self):
        # If no active mission, no focus, and active device has high trust
        if self.scheduler._active_mission:
            return
            
        focus_st, _ = self.scheduler.get_current_focus_state()
        if focus_st.value != "free":
            return
            
        # Check Trust
        conf_score, _ = self.scheduler.get_confidence_info()
        if conf_score > 0.8:
             if self._has_recent_insight(InsightType.IDLE_OPPORTUNITY, 300):
                return
             
             insight = AmbientInsight(
                id=str(uuid.uuid4()),
                type=InsightType.IDLE_OPPORTUNITY,
                description="System is idle with high trust. Good time for proactive maintenance.",
                confidence=0.6,
                is_private=(self.scheduler.get_current_presence_state()[0].value == "with_others")
            )
             self._log_insight(insight)

    def _has_recent_insight(self, type: InsightType, window_seconds: int) -> bool:
        now = time.time()
        for i in self.insights:
            if i.type == type and (now - i.created_at) < window_seconds:
                return True
        return False

    def _log_insight(self, insight: AmbientInsight):
        self.insights.append(insight)
        print(f"[AMBIENT OBSERVER] Insight Generated: [{insight.type.name}] {insight.description}")
        # Audit log could go here via logging module or EventBus
