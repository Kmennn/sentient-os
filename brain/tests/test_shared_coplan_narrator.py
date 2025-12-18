import pytest
from brain.coplanning.shared_policy import SharedPolicy, UserRole
from brain.explainability.shared_coplan_narrator import SharedCoPlanNarrator
from brain.coplanning.shared_coplan import SharedCoPlanProposal
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType

def test_shared_policy_roles():
    policy = SharedPolicy()
    
    # Owner always overrides
    assert policy.can_override(UserRole.OWNER) is True
    assert policy.can_override(UserRole.OPERATOR) is False
    
    # Operator trust gate
    assert policy.can_approve(UserRole.OPERATOR, 0.2) is False
    assert policy.can_approve(UserRole.OPERATOR, 0.8) is True

def test_shared_narrator_status():
    narrator = SharedCoPlanNarrator()
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, "t1", 3600)
    prop = SharedCoPlanProposal("p1", scen, required_approvers=["a", "b"])
    
    # 0/2
    assert "0/2" in narrator.narrate_status(prop)
    
    # 1/2
    prop.approvals["a"] = True
    assert "1/2" in narrator.narrate_status(prop)
    
    # Vetoed
    prop.vetoed = True
    assert "vetoed" in narrator.narrate_status(prop).lower()
