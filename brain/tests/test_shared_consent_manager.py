import pytest
from brain.coplanning.shared_consent_manager import SharedConsentManager
from brain.coplanning.shared_coplan import SharedCoPlanProposal
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType
from brain.coplanning.coplan_proposal import ProposalStatus

def test_shared_consent_quorum():
    manager = SharedConsentManager()
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, "t1", 3600)
    
    # 2 Approvers required
    prop = SharedCoPlanProposal(
        "p1", scen, 
        initiator_user_id="alice",
        required_approvers=["alice", "bob"]
    )
    
    # Alice approves
    manager.register_vote(prop, "alice", True)
    assert manager.check_quorum(prop) is False
    
    # Bob approves
    manager.register_vote(prop, "bob", True)
    assert manager.check_quorum(prop) is True

def test_shared_consent_veto():
    manager = SharedConsentManager()
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, "t1", 3600)
    prop = SharedCoPlanProposal(
        "p1", scen, 
        required_approvers=["alice", "bob"]
    )
    
    # Alice vetoes
    manager.register_vote(prop, "alice", False)
    assert prop.vetoed is True
    assert manager.check_quorum(prop) is False
    
    # Bob tries to approve
    manager.register_vote(prop, "bob", True)
    assert prop.vetoed is True # Still vetoed
    assert manager.check_quorum(prop) is False
