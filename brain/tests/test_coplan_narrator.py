import pytest
from brain.explainability.coplan_narrator import CoPlanNarrator
from brain.coplanning.coplan_proposal import CoPlanProposal, ProposalStatus
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType

def test_coplan_narrator_neutrality():
    narrator = CoPlanNarrator()
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, "t1", 3600)
    proposal = CoPlanProposal("p1", scen, status=ProposalStatus.PENDING)
    
    text = narrator.narrate(proposal)
    assert "ready" in text.lower()
    assert "should" not in text.lower()
    
    proposal.status = ProposalStatus.APPLIED
    text = narrator.narrate(proposal)
    assert "applied" in text.lower()
    assert "undo" in text.lower()
