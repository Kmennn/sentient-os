
import pytest
from brain.missions.mission_scheduler import MissionScheduler, MissionPriority

def test_priority_queueing():
    sched = MissionScheduler()
    sched.schedule("Clean", MissionPriority.BACKGROUND)
    sched.schedule("UserCmd", MissionPriority.USER)
    
    # Tick should pick UserCmd first
    action = sched.tick()
    assert action == "START_NEW"
    assert sched._active_mission.mission_id == "UserCmd"
    
    # Tick again -> No change (UserCmd is running, Clean is lower)
    action = sched.tick()
    assert action is None
    
    # Complete UserCmd
    sched.complete_active()
    
    # Tick -> Should pick Clean
    action = sched.tick()
    assert action == "START_NEW"
    assert sched._active_mission.mission_id == "Clean"

def test_preemption():
    sched = MissionScheduler()
    sched.schedule("Clean", MissionPriority.BACKGROUND)
    
    # Start background
    sched.tick()
    assert sched._active_mission.mission_id == "Clean"
    
    # New high priority arrives
    sched.schedule("Emergency", MissionPriority.CRITICAL)
    
    # Tick -> Should signal Preempt
    action = sched.tick()
    assert action == "PREEMPT"
    # Active should be cleared (put back in queue)
    assert sched._active_mission is None
    
    # Next Tick -> Start Critical
    action = sched.tick()
    assert action == "START_NEW"
    assert sched._active_mission.mission_id == "Emergency"
