import pytest
from brain.missions.mission_scheduler import MissionScheduler
from brain.routines.routine import Routine
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType

def test_scheduler_simulation():
    ms = MissionScheduler()
    # Add a routine
    r = Routine("Static Task", 3600, 3600, [])
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    # Check plan has 1 item
    # snapshot = ms.get_load_snapshot() ...
    
    # Simulate removing it
    scenario = WhatIfScenario("s1", ChangeType.REMOVE_TASK, target_item_id=r.routine_id)
    
    report = ms.simulate_scenario(scenario)
    
    # Expect load score decrease
    assert report.load_score_delta < 0
    # Current state should be unchanged (Routine still there)
    # Re-run simulation check on fresh plan?
    # Verify Scheduler state is untouched
    assert len(list(ms.routine_approval.get_protected_routines())) == 1
