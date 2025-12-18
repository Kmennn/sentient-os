import pytest
import datetime
from brain.missions.mission_scheduler import MissionScheduler
from brain.routines.routine import Routine
from brain.load.load_model import LoadLevel

def test_scheduler_load_snapshot():
    ms = MissionScheduler()
    
    # 1. Setup Routine every day
    r = Routine("Daily Grind", 32400, 3600, [])
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    # 2. Get Snapshot
    snaps = ms.get_load_snapshot()
    
    # 3. Verify
    assert len(snaps) == 7
    # 1 routine = 10 score -> LOW
    assert snaps[0].level == LoadLevel.LOW
