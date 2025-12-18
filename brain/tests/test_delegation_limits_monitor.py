import pytest
from brain.auth.delegation_limits import DelegationLimits
from brain.monitoring.delegation_risk_monitor import DelegationRiskMonitor
from brain.auth.delegation import Delegation, DelegationScope

def test_delegation_limits():
    limits = DelegationLimits()
    ds = [
        Delegation.create("a", "b", DelegationScope.ALL, 3600),
        Delegation.create("a", "c", DelegationScope.ALL, 3600),
        Delegation.create("a", "d", DelegationScope.ALL, 3600),
    ]
    
    # 3 existing, can add more? False (Max 3)
    assert limits.check_limits("a", ds) is False
    
    # Duration check
    assert limits.validate_duration(100) is True
    assert limits.validate_duration(10000000) is False

def test_delegation_chain_detection():
    monitor = DelegationRiskMonitor()
    
    # A -> B
    d1 = Delegation.create("a", "b", DelegationScope.ALL, 3600)
    
    # X -> A (Active)
    d2 = Delegation.create("x", "a", DelegationScope.ALL, 3600)
    
    all_d = [d1, d2]
    
    # Check d1 (A->B). Is there X->A? Yes.
    assert monitor.check_chain(d1, all_d) is True
