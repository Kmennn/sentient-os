
import pytest
from brain.missions.recovery_manager import RecoveryManager
from brain.missions.mission_store import MissionStore
from brain.missions.mission_contract import MissionContract, AutonomyLevel
from brain.tasks.task_graph_runtime import TaskGraphRuntime

def test_recovery_detection():
    store = MissionStore(persistence_path="brain/tests/data/recovery_store.json")
    runtime = TaskGraphRuntime()
    manager = RecoveryManager(store=store, runtime=runtime)
    
    # Save a fake mission
    contract = MissionContract(name="Recov", autonomy_level=AutonomyLevel.EXECUTE)
    store.save_checkpoint(contract, "EXECUTING", 3)
    
    # Check
    data = manager.check_for_recovery()
    assert data is not None
    assert data["current_step_index"] == 3
    assert data["contract"]["name"] == "Recov"
    
    # Perform restore
    manager.perform_recovery(data)
    assert runtime.current_step_index == 3
    
    store.clear()

def test_no_recovery():
    store = MissionStore(persistence_path="brain/tests/data/empty_store.json")
    manager = RecoveryManager(store=store)
    
    assert manager.check_for_recovery() is None
    store.clear()
