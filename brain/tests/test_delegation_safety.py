import pytest
from brain.governance.delegation_escalation_policy import DelegationEscalationPolicy, ApprovalStatus
from brain.explainability.delegation_safety_narrator import DelegationSafetyNarrator
from brain.auth.delegation_limits import DelegationLimits
from brain.monitoring.delegation_risk_monitor import DelegationRiskMonitor
from brain.auth.delegation import Delegation, DelegationScope

def test_escalation_policy_chain_block():
    limits = DelegationLimits()
    monitor = DelegationRiskMonitor()
    policy = DelegationEscalationPolicy(limits, monitor)
    
    # X -> A
    d_x_a = Delegation.create("x", "a", DelegationScope.ALL, 3600)
    # A -> B
    d_a_b = Delegation.create("a", "b", DelegationScope.ALL, 3600)
    
    status = policy.evaluate_delegation_usage(d_a_b, [d_x_a, d_a_b])
    assert status == ApprovalStatus.BLOCKED_CHAIN

def test_safety_narrator():
    narrator = DelegationSafetyNarrator()
    text = narrator.narrate_block(ApprovalStatus.BLOCKED_CHAIN)
    assert "Chain detected" in text
