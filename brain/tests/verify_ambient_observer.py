import sys
import os
import time

sys.path.append(os.getcwd())

# Mock things being imported
from brain.missions.mission_scheduler import mission_scheduler, QueuedMission, MissionPriority
from brain.ambient.ambient_insight import InsightType

def verify_ambient():
    print("=== AMBIENT OBSERVER CHECK ===")
    
    # Reset
    mission_scheduler.ambient_observer.insights = []
    
    # Mock Services to prevent crash in tick()
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    mission_scheduler.suggester = MagicMock()
    mission_scheduler.suggester.check_suggestions.return_value = None
    
    # 1. Test IDLE_OPPORTUNITY
    # Condition: No Active Mission, Focus=Free, Trust > 0.8
    mission_scheduler._active_mission = None
    mission_scheduler.stop_focus_session() # Ensure free
    
    # Fake High Trust (using persistence hack or direct mock if possible, but manager wraps registry)
    # We need a registered device that is active.
    mission_scheduler.device_registry.register_heartbeat("test_dev", "desktop", [])
    # Boost trust manually
    if "test_dev" in mission_scheduler.device_registry._devices:
        d = mission_scheduler.device_registry._devices["test_dev"]
        d.trust_score = 0.9 # High trust
    
    # Mark as active context
    mission_scheduler.active_device_resolver.report_interaction("test_dev", "input")
    
    # TICK
    mission_scheduler.tick()
    
    # Check Insight
    insights = mission_scheduler.ambient_observer.insights
    print(f"Insights generated: {len(insights)}")
    
    has_idle = any(i.type == InsightType.IDLE_OPPORTUNITY for i in insights)
    if has_idle:
        print("PASS: Idle Opportunity Detected.")
        # Print it
        for i in insights:
            if i.type == InsightType.IDLE_OPPORTUNITY:
                print(f" - {i.description} (Conf: {i.confidence})")
    else:
        print("FAIL: Idle Opportunity NOT Detected.")
        # Debug
        st, _ = mission_scheduler.get_current_focus_state()
        print(f"Focus: {st}")
        conf, _ = mission_scheduler.get_confidence_info()
        print(f"Conf: {conf}")
    
    # 2. Test SCHEDULE_PRESSURE
    # Fill Queue
    print("Simulating High Queue...")
    for i in range(6):
        m = QueuedMission(10, time.time(), f"m{i}")
        mission_scheduler._queue.append(m)
        
    # TICK
    mission_scheduler.ambient_observer._last_check = 0 # Force tick
    mission_scheduler.tick()
    
    insights = mission_scheduler.ambient_observer.insights
    has_pressure = any(i.type == InsightType.SCHEDULE_PRESSURE for i in insights)
    
    if has_pressure:
        print("PASS: Schedule Pressure Detected.")
    else:
        print("FAIL: Schedule Pressure NOT Detected.")
        print(f"Queue Len: {len(mission_scheduler._queue)}")

    # Clean up
    mission_scheduler._queue = []

if __name__ == "__main__":
    verify_ambient()
