import pytest
from brain.missions.mission_scheduler import MissionScheduler
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType
from brain.routines.routine import Routine
from brain.coplanning.coplan_proposal import ProposalStatus

def test_scheduler_coplan_lifecycle():
    ms = MissionScheduler()
    r = Routine("CoPlan Task", 3600, 3600, [])
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    # Create Proposal: Move to 2:00
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, r.routine_id, 7200)
    proposal = ms.create_proposal_from_scenario(scen)
    
    # Status PENDING
    assert proposal.status == ProposalStatus.PENDING
    
    # Apply
    success = ms.apply_coplan_proposal(proposal)
    assert success is True
    assert r.time_of_day_seconds == 7200
    
    # Undo
    success = ms.undo_coplan_proposal(proposal)
    assert success is True
    assert r.time_of_day_seconds == 3600
