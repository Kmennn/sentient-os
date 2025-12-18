import pytest
import time
from brain.missions.mission_scheduler import MissionScheduler, MissionPriority
from brain.missions.mission_contract import MissionContract
from brain.auth.role import UserRole

def test_deferral_on_conflict():
    ms = MissionScheduler()
    
    # 1. Active Owner Mission
    c1 = MissionContract(created_by="owner", execution_role=UserRole.OWNER, allowed_objects=["res"])
    ms.schedule("m1", MissionPriority.USER, payload=c1)
    ms.tick() # m1 active
    
    # 2. Operator Mission (Normally REJECTED, but now check Deferral)
    c2 = MissionContract(created_by="op", execution_role=UserRole.OPERATOR, allowed_objects=["res"])
    
    # Schedule m2
    # Should be "REJECT_NEW" by policy, then "DELAY" by engine (default Flexible)
    # So it should be SCHEDULED (but blocked)
    # wait, my code says `return "SCHEDULED"` at end if it passes logic.
    ms.schedule("m2", MissionPriority.USER, payload=c2)
    
    # Check queue
    assert len(ms._queue) == 1
    m2_entry = ms._queue[0]
    assert m2_entry.mission_id == "m2"
    assert m2_entry.blocked_until > time.time()
    
    # Tick should not start m2 yet (blocked)
    res = ms.tick()
    assert res is None # No change
    assert ms._active_mission.mission_id == "m1"
