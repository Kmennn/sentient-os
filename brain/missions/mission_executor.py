
import logging
from typing import Optional, List, Dict
from brain.missions.mission_contract import MissionContract, AutonomyLevel
from brain.safety.mission_enforcer import MissionEnforcer, MissionViolationError
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, AutonomyState, autonomy_state_machine
from brain.missions.escalation_engine import EscalationEngine, EscalationLevel, escalation_engine
from brain.tasks.task_graph_runtime import TaskGraphRuntime, task_graph_runtime
from brain.missions.mission_store import MissionStore, mission_store
from brain.autonomy.trust_weighted_controller import TrustWeightedController, trust_weighted_controller

logger = logging.getLogger(__name__)

class MissionExecutor:
    """
    Orchestrates the mission execution loop.
    1. Validates Contract
    2. Checks State
    3. Executes Step (via Runtime)
    4. Persists State
    """
    def __init__(self, 
                 state_machine: AutonomyStateMachine = autonomy_state_machine,
                 escalation: EscalationEngine = escalation_engine,
                 runtime: TaskGraphRuntime = task_graph_runtime,
                 store: MissionStore = mission_store,
                 trust_ctrl: TrustWeightedController = trust_weighted_controller):
        self.sm = state_machine
        self.escalation = escalation
        self.runtime = runtime
        self.store = store
        self.trust_ctrl = trust_ctrl
        self.current_contract: Optional[MissionContract] = None
        self.enforcer: Optional[MissionEnforcer] = None
        
    def start_mission(self, contract: MissionContract, steps: List[Dict] = None):
        """
        Start mission with a list of steps (simulating a Graph).
        """
        if self.sm.state != AutonomyState.IDLE:
             logger.warning("Cannot start mission: System not IDLE.")
             return
             
        self.current_contract = contract
        self.enforcer = MissionEnforcer(contract)
        
        # Load tasks
        if steps:
            self.runtime.load_graph(steps)
        
        # Transitions
        self.sm.transition(AutonomyState.PLANNING)
        self.sm.transition(AutonomyState.EXECUTING)
        
        # Persist Initial State
        self.store.save_checkpoint(contract, "EXECUTING", 0)
            
    def step(self):
        """
        Execute a single step from the runtime.
        """
        if self.sm.state != AutonomyState.EXECUTING:
            return "Not Executing"
            
        # Get next step
        step_data = self.runtime.next_step()
        if step_data is None:
            self.sm.transition(AutonomyState.COMPLETED)
            return "Mission Complete"
            
        action = step_data['action']
        object_id = step_data['object_id']
            
        # 1. Enforce
        try:
            self.enforcer.validate_action(action, object_id)
        except MissionViolationError as e:
            self.escalation.escalate(str(e), EscalationLevel.CRITICAL)
            return "Violation"
            
        # 2. Check Autonomy Level (Trust-Weighted)
        # We ask the controller if we should pause based on Contract + Trust.
        # This covers both 'Assist Mode' contract AND 'Low Trust' override.
        if self.trust_ctrl.should_pause_for_confirmation(self.current_contract.autonomy_level):
            # In Assist mode (or Downgraded), we must Pause and ask
            # Revert step index so we retry this step next time
            self.runtime.set_step_index(self.runtime.current_step_index - 1)
            
            reason = "Approval Required"
            if self.current_contract.autonomy_level == AutonomyLevel.ASSIST:
                reason += " (Assist Mode)"
            else:
                reason += " (Trust/Policy Downgrade)"
                
            self.escalation.escalate(reason, EscalationLevel.WARNING)
            return "Paused for Approval"
            
        # 3. Execute logic (Hybrid Planner v3.3 invoked here in real system)
        logger.info(f"EXECUTING: {action} on {object_id}")
        
        # 4. Persist
        self.store.save_checkpoint(self.current_contract, "EXECUTING", self.runtime.current_step_index)
        
        return "Done"

mission_executor = MissionExecutor()
