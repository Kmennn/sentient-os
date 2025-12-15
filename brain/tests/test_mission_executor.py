
import pytest
from brain.missions.mission_executor import MissionExecutor
from brain.missions.mission_contract import MissionContract, AutonomyLevel
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, AutonomyState
from brain.missions.escalation_engine import EscalationEngine
from brain.tasks.task_graph_runtime import TaskGraphRuntime
from brain.missions.mission_store import MissionStore

@pytest.fixture
def executor_setup():
    sm = AutonomyStateMachine()
    esc = EscalationEngine(sm)
    runtime = TaskGraphRuntime()
    store = MissionStore(persistence_path="brain/tests/data/unit_executor_store.json") # separate store
    exc = MissionExecutor(state_machine=sm, escalation=esc, runtime=runtime, store=store)
    return exc, sm, runtime, store

def test_mission_lifecycle(executor_setup):
    exc, sm, runtime, store = executor_setup
    
    contract = MissionContract(
        allowed_actions=["pick"],
        allowed_objects=["cup"],
        autonomy_level=AutonomyLevel.EXECUTE
    )
    
    steps = [{"action": "pick", "object_id": "cup"}]
    
    exc.start_mission(contract, steps)
    assert sm.state == AutonomyState.EXECUTING
    
    # Valid Step
    res = exc.step()
    assert res == "Done"
    
    # Check Completion logic if we call step again
    res = exc.step() 
    assert res == "Mission Complete"
    assert sm.state == AutonomyState.COMPLETED
    
    store.clear()

def test_assist_mode_pause(executor_setup):
    exc, sm, runtime, store = executor_setup
    
    contract = MissionContract(
        allowed_actions=["pick"],
        allowed_objects=["cup"],
        autonomy_level=AutonomyLevel.ASSIST
    )
    
    steps = [{"action": "pick", "object_id": "cup"}]
    
    exc.start_mission(contract, steps)
    
    # Step should trigger warning/escalation because of ASSIST mode
    res = exc.step()
    assert res == "Paused for Approval"
    
    # State should remain EXECUTING but paused logic... 
    # Actually validation logic in executor usually keeps it executing but returns paused string.
    # The EscalationEngine might trigger ESCALATED state if level is WARNING.
    # Let's check State Machine.
    # Escalation WARNING -> ESCALATED state transition is defined in EscalationEngine
    assert sm.state == AutonomyState.ESCALATED
    store.clear()
