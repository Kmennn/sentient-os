import pytest
from brain.governance.temporal_policy import TemporalPolicy
from brain.auth.role import UserRole
from brain.intents.intent import Intent

def test_owner_powers():
    tp = TemporalPolicy()
    owner_intent = Intent("u1", UserRole.OWNER, "Run")
    op_intent = Intent("u2", UserRole.OPERATOR, "Run")
    
    # Owner can defer everyone
    assert tp.can_defer(UserRole.OWNER, owner_intent)
    assert tp.can_defer(UserRole.OWNER, op_intent)

def test_operator_powers():
    tp = TemporalPolicy()
    owner_intent = Intent("u1", UserRole.OWNER, "Run")
    op_intent = Intent("u2", UserRole.OPERATOR, "Run")
    
    # Operator cannot defer Owner
    assert not tp.can_defer(UserRole.OPERATOR, owner_intent)
    
    # Operator can defer Operator
    assert tp.can_defer(UserRole.OPERATOR, op_intent)

def test_observer_powers():
    tp = TemporalPolicy()
    op_intent = Intent("u2", UserRole.OPERATOR, "Run")
    
    assert not tp.can_defer(UserRole.OBSERVER, op_intent)
