import pytest
import time
from brain.auth.delegation import Delegation, DelegationScope
from brain.governance.delegation_policy import DelegationPolicy

def test_delegation_lifecycle():
    policy = DelegationPolicy()
    
    # Alice delegates to Bob for 1 hour
    d = Delegation.create("alice", "bob", DelegationScope.ALL, 3600)
    policy.add_delegation(d)
    
    # Check Authority
    assert policy.check_authority("alice", "alice") is True # Self
    assert policy.check_authority("bob", "alice") is True # Delegate
    assert policy.check_authority("charlie", "alice") is False # Random
    
    # Revoke
    policy.revoke_delegation(d.delegation_id)
    assert policy.check_authority("bob", "alice") is False # Revoked

def test_delegation_expiry():
    policy = DelegationPolicy()
    # Expired delegation (created 2 hours ago, lasted 1 hour)
    d = Delegation.create("alice", "bob", DelegationScope.ALL, 3600)
    d.expires_at = time.time() - 10 # Force expire
    policy.add_delegation(d)
    
    assert policy.check_authority("bob", "alice") is False
