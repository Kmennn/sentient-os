
import pytest
from brain.missions.mission_executor import MissionExecutor
from brain.missions.mission_contract import MissionContract, AutonomyLevel
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, AutonomyState
from brain.missions.escalation_engine import EscalationEngine
from brain.tasks.task_graph_runtime import TaskGraphRuntime
from brain.missions.mission_store import MissionStore

def test_integration_flow():
    sm = AutonomyStateMachine()
    esc = EscalationEngine(sm)
    curr_runtime = TaskGraphRuntime()
    store = MissionStore(persistence_path="brain/tests/data/integration_store.json")
    
    exc = MissionExecutor(sm, esc, runtime=curr_runtime, store=store)
    
    contract = MissionContract(
        allowed_actions=["pick", "place"],
        allowed_objects=["cup", "table"],
        autonomy_level=AutonomyLevel.EXECUTE
    )
    
    steps = [
        {"action": "pick", "object_id": "cup"},
        {"action": "place", "object_id": "table"}
    ]
    
    exc.start_mission(contract, steps)
    assert sm.state == AutonomyState.EXECUTING
    
    # Step 1
    res = exc.step()
    assert res == "Done"
    assert curr_runtime.current_step_index == 1
    
    # Verify Persistence
    data = store.load_active_mission()
    assert data["current_step_index"] == 1
    
    # Step 2
    res = exc.step()
    assert res == "Done"
    
    # Step 3 (Done)
    res = exc.step()
    assert res == "Mission Complete"
    assert sm.state == AutonomyState.COMPLETED
