
import pytest
import time
from brain.missions.mission_contract import MissionContract, AutonomyLevel
from dataclasses import FrozenInstanceError

def test_contract_immutability():
    contract = MissionContract(name="Test")
    
    # Try to modify name
    with pytest.raises(FrozenInstanceError):
        contract.name = "New Name"
        
    # Try to modify scope
    # Note: Lists are mutable in Python even in frozen dataclasses unless tuples are used.
    # ideally we should use tuples for strict immutability, but usually the reference check is enough for basic safety.
    # However, replacing the list should fail.
    with pytest.raises(FrozenInstanceError):
        contract.allowed_actions = ["hack"]

def test_expiration():
    contract = MissionContract(max_duration=0.1)
    assert not contract.is_expired()
    time.sleep(0.2)
    assert contract.is_expired()

def test_defaults():
    contract = MissionContract()
    assert contract.autonomy_level == AutonomyLevel.ASSIST
    assert contract.mission_id is not None
