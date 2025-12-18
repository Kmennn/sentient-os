import pytest
from brain.missions.mission_contract import MissionContract
from brain.auth.role import UserRole
from brain.auth.user import User

def test_contract_metadata_defaults():
    c = MissionContract()
    assert c.created_by is None
    assert c.approved_by is None
    assert c.execution_role is None

def test_contract_authority_validation():
    # Mission strictly for OPERATOR
    c = MissionContract(execution_role=UserRole.OPERATOR)
    
    # Operator should pass (logic strictly checks equality in base impl, but let's see my implementation)
    # Actually my implementation says: if execution_role and execution_role != user_role: if OWNER return True else False
    # So OPERATOR == OPERATOR -> True (loop doesn't enter)
    
    assert c.validate_authority(UserRole.OPERATOR)
    assert c.validate_authority(UserRole.OWNER) # Owner overrides
    assert not c.validate_authority(UserRole.OBSERVER)

def test_explicit_assignment():
    alice = User(name="Alice", role=UserRole.OWNER)
    bob = User(name="Bob", role=UserRole.OPERATOR)
    
    c = MissionContract(
        name="Critical Fix",
        created_by=alice.user_id,
        approved_by=alice.user_id,
        execution_role=UserRole.OPERATOR
    )
    
    assert c.created_by == alice.user_id
    assert c.approved_by == alice.user_id
    assert c.execution_role == UserRole.OPERATOR
