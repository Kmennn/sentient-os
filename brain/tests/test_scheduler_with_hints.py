import pytest
import time
from brain.missions.mission_scheduler import MissionScheduler, MissionPriority, QueuedMission
from brain.optimization.mission_optimizer import OptimizationHint, OptimizationAction

@pytest.fixture
def scheduler():
    return MissionScheduler()

def test_schedule_delay_hint(scheduler):
    # Schedule with 1s delay
    hint = OptimizationHint(OptimizationAction.SCHEDULE_DELAY, "test", "reason", parameter=1.0)
    scheduler.schedule("m1", MissionPriority.USER, hints=[hint])
    
    # Tick immediately -> Should receive None (blocked)
    assert scheduler.tick() is None
    
    # Wait > 1s
    time.sleep(1.1)
    
    # Tick -> Should start
    assert scheduler.tick() == "START_NEW"
    assert scheduler._active_mission.mission_id == "m1"

def test_avoid_concurrency_prevents_preemption(scheduler):
    # Start a LOW priority mission
    scheduler.schedule("low_pri", MissionPriority.BACKGROUND)
    scheduler.tick()
    assert scheduler._active_mission.mission_id == "low_pri"
    
    # Schedule HIGH priority with AVOID_CONCURRENCY hint
    # (Pretend logic: High pri mission is fragile and shouldn't interrupt others)
    hint = OptimizationHint(OptimizationAction.AVOID_CONCURRENCY, "high_pri", "reason")
    scheduler.schedule("high_pri", MissionPriority.USER, hints=[hint])
    
    # Tick -> Should NOT preempt
    assert scheduler.tick() is None
    assert scheduler._active_mission.mission_id == "low_pri"
    
    # Complete active
    scheduler.complete_active()
    
    # Tick -> Should start HIGH
    assert scheduler.tick() == "START_NEW"
    assert scheduler._active_mission.mission_id == "high_pri"
