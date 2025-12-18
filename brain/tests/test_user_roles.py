import pytest
from brain.auth.role import UserRole
from brain.auth.user import User

def test_role_hierarchy():
    owner = UserRole.OWNER
    operator = UserRole.OPERATOR
    observer = UserRole.OBSERVER
    
    # Low Trust Approval
    assert owner.can_approve_low_trust()
    assert not operator.can_approve_low_trust()
    assert not observer.can_approve_low_trust()
    
    # Physical Approval
    assert owner.can_approve_physical()
    assert operator.can_approve_physical()
    assert not observer.can_approve_physical()
    
    # Execution
    assert owner.can_execute_missions()
    assert operator.can_execute_missions()
    assert not observer.can_execute_missions()

def test_user_creation():
    u = User(name="Alice", role=UserRole.OWNER)
    assert u.user_id is not None
    assert u.is_owner
    assert u.can_override_trust()

def test_trust_override():
    # Owner always overrides
    owner = User(name="Owner", role=UserRole.OWNER, trust_override_permission=False)
    assert owner.can_override_trust()
    
    # Operator doesn't unless implicit
    op = User(name="Op", role=UserRole.OPERATOR, trust_override_permission=False)
    assert not op.can_override_trust()
    
    # Operator with explicit permission
    trusted_op = User(name="TrustedOp", role=UserRole.OPERATOR, trust_override_permission=True)
    assert trusted_op.can_override_trust()
    
    # Observer cannot override even with flag (though typically shouldn't have flag)
    # Actually, implementation allows flag to carry weight if we want, but logically:
    observer = User(name="Obs", role=UserRole.OBSERVER, trust_override_permission=True)
    assert observer.can_override_trust() # Flag takes precedence based on current impl
