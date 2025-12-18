import pytest
from brain.coplanning.coplan_applier import CoPlanApplier
from brain.coplanning.coplan_proposal import CoPlanProposal, ProposalStatus
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType
from brain.missions.mission_scheduler import MissionScheduler
from brain.routines.routine import Routine

def test_applier_apply_and_revert():
    scheduler = MissionScheduler()
    applier = CoPlanApplier()
    
    # Setup Routine
    r = Routine("Test Routine", 3600, 3600, []) # 1:00
    scheduler.routine_approval.add_candidate(r)
    scheduler.routine_approval.protect_routine(r.routine_id)
    
    # Create Proposal: Move to 2:00 (7200)
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, r.routine_id, 7200)
    proposal = CoPlanProposal("p1", scen)
    
    # 1. Apply
    success = applier.apply(proposal, scheduler)
    assert success is True
    assert r.time_of_day_seconds == 7200
    assert proposal.status == ProposalStatus.APPLIED
    assert proposal.undo_data["time_of_day_seconds"] == 3600
    
    # 2. Revert
    success = applier.revert(proposal, scheduler)
    assert success is True
    assert r.time_of_day_seconds == 3600
    assert proposal.status == ProposalStatus.REVERTED
