import pytest
from brain.governance.approval_policy import ApprovalPolicy
from brain.auth.user import User
from brain.auth.role import UserRole
from brain.missions.mission_contract import MissionContract

def test_observer_cannot_approve():
    obs = User(name="Obs", role=UserRole.OBSERVER)
    c = MissionContract()
    assert not ApprovalPolicy.can_approve(obs, c)
    assert "Observers cannot approve" in ApprovalPolicy.get_denial_reason(obs, c)

def test_owner_powers():
    owner = User(name="Owner", role=UserRole.OWNER)
    c = MissionContract()
    
    # Can approve regular
    assert ApprovalPolicy.can_approve(owner, c)
    
    # Can approve low trust
    assert ApprovalPolicy.can_approve(owner, c, is_low_trust_context=True)
    
    # Can approve physical
    assert ApprovalPolicy.can_approve(owner, c, has_physical_actions=True)

def test_operator_limitations():
    op = User(name="Op", role=UserRole.OPERATOR)
    c = MissionContract()
    
    # Can approve regular
    assert ApprovalPolicy.can_approve(op, c)
    
    # Cannot approve low trust
    assert not ApprovalPolicy.can_approve(op, c, is_low_trust_context=True)
    
    # Can approve physical
    assert ApprovalPolicy.can_approve(op, c, has_physical_actions=True)

def test_execution_role_escalation():
    op = User(name="Op", role=UserRole.OPERATOR)
    
    # Contract requires OWNER execution
    c_owner = MissionContract(execution_role=UserRole.OWNER)
    
    # Operator cannot approve a mission that requires OWNER execution
    assert not ApprovalPolicy.can_approve(op, c_owner)
    
    # Owner can
    owner = User(name="Owner", role=UserRole.OWNER)
    assert ApprovalPolicy.can_approve(owner, c_owner)
