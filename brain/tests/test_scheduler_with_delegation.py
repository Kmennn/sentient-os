import pytest
import time
from brain.missions.mission_scheduler import MissionScheduler
from brain.coplanning.shared_coplan import SharedCoPlanProposal
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType
from brain.auth.delegation import Delegation, DelegationScope

def test_scheduler_delegation_voting():
    ms = MissionScheduler()
    
    # 1. Setup Delegation: Alice -> Bob
    d = Delegation.create("alice", "bob", DelegationScope.ALL, 3600)
    ms.delegation_policy.add_delegation(d)
    
    # 2. Proposal requiring Alice
    scen = WhatIfScenario("s1", ChangeType.MOVE_TASK, "t1", 3600)
    prop = SharedCoPlanProposal("p1", scen, required_approvers=["alice"])
    
    # 3. Bob votes (Delegated)
    ms.register_coplan_vote(prop, "bob", True)
    
    # 4. Check if Alice's approval is registered
    assert prop.approvals.get("alice") is True
    
def test_scheduler_delegation_expiry():
    ms = MissionScheduler()
    d = Delegation.create("alice", "bob", DelegationScope.ALL, 3600)
    d.expires_at = time.time() - 10
    ms.delegation_policy.add_delegation(d)
    
    prop = SharedCoPlanProposal("p1", None, required_approvers=["alice"])
    
    # Bob votes (Expired)
    ms.register_coplan_vote(prop, "bob", True)
    
    # Check
    assert prop.approvals.get("alice") is None # No vote registered
