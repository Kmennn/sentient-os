
import pytest
import os
import json
from brain.missions.mission_store import MissionStore
from brain.missions.mission_contract import MissionContract, AutonomyLevel

TEST_DB_PATH = "brain/tests/data/test_mission_store.json"

@pytest.fixture
def store():
    s = MissionStore(persistence_path=TEST_DB_PATH)
    yield s
    s.clear()
    if os.path.exists(os.path.dirname(TEST_DB_PATH)):
        # clean up dir if empty? not strictly needed for test
        pass

def test_save_load(store):
    contract = MissionContract(
        name="Persistence Test",
        allowed_actions=["test"],
        autonomy_level=AutonomyLevel.EXECUTE
    )
    
    store.save_checkpoint(contract, "EXECUTING", 5)
    
    data = store.load_active_mission()
    assert data is not None
    assert data["mission_id"] == contract.mission_id
    assert data["state"] == "EXECUTING"
    assert data["current_step_index"] == 5
    assert data["contract"]["autonomy_level"] == "EXECUTE"

def test_load_empty(store):
    data = store.load_active_mission()
    assert data is None

def test_clear(store):
    contract = MissionContract(name="T")
    store.save_checkpoint(contract, "A", 1)
    store.clear()
    assert store.load_active_mission() is None
