
import pytest
from brain.missions.mission_preemption import PreemptionHandler
from brain.missions.mission_executor import MissionExecutor
from brain.missions.mission_store import MissionStore
from brain.missions.mission_contract import MissionContract, AutonomyLevel
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, AutonomyState
from brain.tasks.task_graph_runtime import TaskGraphRuntime
from brain.missions.escalation_engine import EscalationEngine

def test_preemption_flow():
    # Setup Executor
    sm = AutonomyStateMachine()
    esc = EscalationEngine(sm)
    runtime = TaskGraphRuntime()
    store = MissionStore(persistence_path="brain/tests/data/preempt_store.json")
    exc = MissionExecutor(state_machine=sm, runtime=runtime, store=store, escalation=esc)
    
    handler = PreemptionHandler(executor=exc, store=store)
    
    # Start Mission
    contract = MissionContract(name="LongJob", autonomy_level=AutonomyLevel.EXECUTE)
    exc.start_mission(contract, [{"action": "a", "object_id": "o"}])
    
    assert sm.state == AutonomyState.EXECUTING
    
    # Preempt
    success = handler.preempt_active_mission()
    assert success
    assert sm.state == AutonomyState.PAUSED
    
    # Verify Store has PAUSED state
    data = store.load_active_mission()
    assert data["state"] == "PAUSED"
    
    store.clear()
