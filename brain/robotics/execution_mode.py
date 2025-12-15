
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class Mode(Enum):
    SIMULATION = "SIMULATION"
    DRY_RUN = "DRY_RUN"
    LIVE = "LIVE"

class ExecutionModeManager:
    """
    Safety Gate for Robotics Execution.
    """
    def __init__(self):
        self._current_mode = Mode.SIMULATION
        self.is_estop_active = False

    def set_mode(self, mode_str: str) -> bool:
        if self.is_estop_active:
            logger.error("Cannot change mode while E-STOP is active!")
            return False
            
        try:
            new_mode = Mode(mode_str)
            
            # Additional checks for LIVE
            if new_mode == Mode.LIVE:
                logger.warning("Switching to LIVE mode. REAL HARDWARE WILL MOVE.")
                
            self._current_mode = new_mode
            logger.info(f"Execution Mode set to: {self._current_mode.value}")
            return True
        except ValueError:
            logger.error(f"Invalid mode: {mode_str}")
            return False

    def get_mode(self) -> Mode:
        return self._current_mode

    def trigger_estop(self):
        self.is_estop_active = True
        self._current_mode = Mode.SIMULATION # Fallback safety
        logger.critical("E-STOP TRIGGERED! System fallback to SIMULATION.")

    def clear_estop(self):
        self.is_estop_active = False
        logger.info("E-STOP Cleared.")

    def validate_action(self) -> bool:
        if self.is_estop_active:
            logger.error("Action blocked: E-STOP Active.")
            return False
            
        # In SIMULATION and DRY_RUN, actions are "safe" (mocked or disconnected)
        # In LIVE, we allow action but it implies real risk
        return True

execution_manager = ExecutionModeManager()
