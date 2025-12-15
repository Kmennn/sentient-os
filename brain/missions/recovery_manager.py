
import logging
from typing import Optional, Dict
from brain.missions.mission_store import MissionStore, mission_store
from brain.missions.mission_contract import MissionContract, AutonomyLevel
from brain.tasks.task_graph_runtime import TaskGraphRuntime, task_graph_runtime
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, autonomy_state_machine

logger = logging.getLogger(__name__)

class RecoveryManager:
    """
    Handles system restart recovery.
    Checks for persisted mission state and prepares system for Resume.
    """
    def __init__(self, 
                 store: MissionStore = mission_store,
                 runtime: TaskGraphRuntime = task_graph_runtime,
                 sm: AutonomyStateMachine = autonomy_state_machine):
        self.store = store
        self.runtime = runtime
        self.sm = sm
        
    def check_for_recovery(self) -> Optional[Dict]:
        """
        Check if there was an active mission.
        If yes, load it but keep state PAUSED/Idle until user confirms.
        Returns recovery info if found.
        """
        data = self.store.load_active_mission()
        if not data:
            return None
            
        logger.info(f"Recovery Found: Mission {data['mission_id']} at Step {data['current_step_index']}")
        
        # Hydrate components?
        # In a real system, we'd need to reconstruct the Contract object fully.
        # For now, we return data so UI can prompt user.
        return data
        
    def perform_recovery(self, recovery_data: Dict):
        """
        User confirmed resume. 
        Restore runtime state.
        """
        step_index = recovery_data['current_step_index']
        self.runtime.set_step_index(step_index)
        
        # Restore SM state?
        # We probably want to start in PAUSED/ESCALATED so user must hit Play.
        # Can't jump to PAUSED from IDLE directly in our SM?
        # IDLE -> PLANNING -> EXECUTING -> PAUSED
        # We might need a special transition for Recovery?
        # Or just tell user "Ready to Resume" and let them click Start?
        # Let's say we leave it in IDLE but pre-loaded.
        pass

recovery_manager = RecoveryManager()
