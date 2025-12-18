import pytest
import time
from brain.missions.mission_scheduler import MissionScheduler, MissionPriority
from brain.missions.mission_contract import MissionContract
from brain.routines.routine import Routine
from brain.auth.role import UserRole

def test_routine_deferral():
    ms = MissionScheduler()
    
    # 1. Protect a "Morning Routine" right now
    # Mock time?
    # Routine Approval is in ms.routine_approval
    
    import datetime
    now = datetime.datetime.now()
    secs = now.hour * 3600 + now.minute * 60 + now.second
    
    # Routine starts 10s ago, lasts 60s (so we are inside it)
    r = Routine("Morning Routine", secs - 10, 60, [0,1,2,3,4,5,6], protected=True)
    ms.routine_approval.protected[r.routine_id] = r
    
    # 2. Schedule a normal mission
    c = MissionContract(created_by="u1", execution_role=UserRole.OPERATOR, allowed_objects=[])
    
    ms.schedule("m1", MissionPriority.USER, payload=c)
    
    # Validation: Should be queued with blocked_until
    assert len(ms._queue) == 1
    m = ms._queue[0]
    
    # Should perform blocked wait
    assert m.blocked_until > time.time()
    
    # Should NOT be active yet
    ms.tick()
    assert ms._active_mission is None

def test_emergency_bypasses_routine():
    ms = MissionScheduler()
    import datetime
    now = datetime.datetime.now()
    secs = now.hour * 3600 + now.minute * 60 + now.second
    
    r = Routine("Morning Routine", secs - 10, 60, [0,1,2,3,4,5,6], protected=True)
    ms.routine_approval.protected[r.routine_id] = r
    
    # CRITICAL priority -> Emergency Intent
    c = MissionContract(created_by="owner", execution_role=UserRole.OWNER, allowed_objects=[])
    
    ms.schedule("m_emerg", MissionPriority.CRITICAL, payload=c)
    
    # Should run immediately
    ms.tick()
    assert ms._active_mission.mission_id == "m_emerg"
