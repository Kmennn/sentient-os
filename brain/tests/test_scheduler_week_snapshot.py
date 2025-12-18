import pytest
import datetime
from brain.missions.mission_scheduler import MissionScheduler
from brain.routines.routine import Routine

def test_scheduler_week_snapshot():
    ms = MissionScheduler()
    
    # 1. Setup Routine every day (default Routine has empty days list which Planner might interpret?
    # v5.0 Planner: `if r.days_of_week: if date.weekday() not in r.days_of_week: continue`
    # Empty list = Every day? Or No days?
    # Logic in Planner: `if hasattr(r, 'days_of_week') and r.days_of_week:`
    # If list is empty, condition `and r.days_of_week` is False, so it skips the check => Every day.
    
    r = Routine("Daily Standup", 32400, 1800, []) # Empty = Daily
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    # 2. Get Snapshot
    wk = ms.get_week_snapshot()
    
    # 3. Verify
    # Should have 7 days
    assert len(wk.days) == 7
    
    # Should detect ROUTINE_HEAVY because we have 7 days * 1 routine = 7 routines.
    # Analyzer threshold is > 10.
    # Let's add another routine to trigger it.
    
    r2 = Routine("Evening Review", 61200, 1800, [])
    ms.routine_approval.add_candidate(r2)
    ms.routine_approval.protect_routine(r2.routine_id)
    
    # Now 14 routines total > 10
    wk = ms.get_week_snapshot()
    
    heavy = next((p for p in wk.patterns if p.type == "ROUTINE_HEAVY"), None)
    assert heavy is not None
