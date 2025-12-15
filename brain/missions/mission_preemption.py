
import logging
from brain.missions.mission_executor import MissionExecutor, mission_executor
from brain.missions.mission_store import MissionStore, mission_store
from brain.autonomy.autonomy_state_machine import AutonomyState

logger = logging.getLogger(__name__)

class PreemptionHandler:
    """
    Handles the safe preemption of the active mission.
    Ensures state is saved and execution is cleanly paused.
    """
    def __init__(self, executor: MissionExecutor = mission_executor, store: MissionStore = mission_store):
        self.executor = executor
        self.store = store
        
    def preempt_active_mission(self) -> bool:
        """
        Attempts to pause the current mission.
        Returns True if successful (safely paused).
        """
        contract = self.executor.current_contract
        if not contract:
            return True # Nothing to preempt
            
        # 1. Check if safe to pause (Atomic steps assumption for now)
        # In real system, we might need to retract arm, etc.
        logger.info(f"Preempting Mission {contract.mission_id}...")
        
        # 2. Transition State Machine
        if self.executor.sm.state == AutonomyState.EXECUTING:
            self.executor.sm.transition(AutonomyState.PAUSED)
            
        # 3. Persist State immediatey
        step_idx = self.executor.runtime.current_step_index
        self.store.save_checkpoint(contract, "PAUSED", step_idx)
        
        logger.info(f"Mission {contract.mission_id} paused at step {step_idx} for preemption.")
        return True

preemption_handler = PreemptionHandler()
