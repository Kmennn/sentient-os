import pytest
import datetime
import time
from brain.missions.mission_scheduler import MissionScheduler, QueuedMission
from brain.routines.routine import Routine

def test_scheduler_day_snapshot():
    ms = MissionScheduler()
    
    # Setup Routine
    r = Routine("Morning Focus", 32400, 3600, [])
    # Hack: Add to protected directly or via approval
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    # Setup Scheduled Task
    # blocked_until = Now + 1h
    now = time.time()
    task = QueuedMission(10, now, "task1", blocked_until=now + 3600)
    import heapq
    heapq.heappush(ms._queue, task)
    
    # Get Snapshot
    plan = ms.get_day_snapshot()
    
    # Verify
    assert len(plan.items) >= 2
    
    r_found = any(i.type == 'ROUTINE' and i.name == "Morning Focus" for i in plan.items)
    t_found = any(i.type == 'TASK' and i.id == "task1" for i in plan.items)
    
    assert r_found
    assert t_found
