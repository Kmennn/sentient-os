import pytest
from brain.missions.mission_scheduler import MissionScheduler
from brain.coplanning.shared_coplan import SharedCoPlanProposal
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType
from brain.routines.routine import Routine

def test_scheduler_shared_voting_flow():
    ms = MissionScheduler()
    r = Routine("Shared Task", 3600, 3600, [])
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    # Create Shared Proposal (Manual creation as engine doesn't do shared yet)
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, r.routine_id, 7200)
    proposal = SharedCoPlanProposal(
        "p1", scen, 
        required_approvers=["alice", "bob"]
    )
    
    # 1. Try Apply (Should Fail - No Votes)
    assert ms.apply_coplan_proposal(proposal) is False
    
    # 2. Alice Approves
    ms.register_coplan_vote(proposal, "alice", True)
    assert ms.apply_coplan_proposal(proposal) is False # Bob missing
    
    # 3. Bob Approves
    ms.register_coplan_vote(proposal, "bob", True)
    
    # 4. Try Apply (Should Succeed)
    assert ms.apply_coplan_proposal(proposal) is True
    assert r.time_of_day_seconds == 7200
