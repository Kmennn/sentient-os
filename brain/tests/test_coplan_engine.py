import pytest
from brain.coplanning.coplan_engine import CoPlanEngine
from brain.coplanning.coplan_proposal import ProposalStatus
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType

def test_proposal_creation():
    engine = CoPlanEngine()
    scenario = WhatIfScenario("s1", ChangeType.MOVE_TASK, "t1", 3600)
    
    proposal = engine.create_proposal(scenario)
    
    assert proposal.status == ProposalStatus.PENDING
    assert proposal.scenario.scenario_id == "s1"
    assert proposal.proposal_id is not None
