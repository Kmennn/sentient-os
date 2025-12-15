
import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)

class AutonomyState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    PAUSED = auto()
    ESCALATED = auto() # Waiting for user
    COMPLETED = auto()
    ABORTED = auto()

class InvalidTransitionError(Exception):
    pass

class AutonomyStateMachine:
    """
    Manages the high-level state of the autonomy engine.
    Enforces valid transitions.
    """
    def __init__(self):
        self._state = AutonomyState.IDLE
        
    @property
    def state(self):
        return self._state
        
    def transition(self, target_state: AutonomyState):
        """
        Attempt to transition to target_state.
        Raises InvalidTransitionError if illegal.
        """
        if target_state == self._state:
            return
            
        valid = False
        
        # Define allowed transitions
        # From IDLE
        if self._state == AutonomyState.IDLE:
             if target_state in [AutonomyState.PLANNING]: valid = True
             
        # From PLANNING
        elif self._state == AutonomyState.PLANNING:
            if target_state in [AutonomyState.EXECUTING, AutonomyState.ABORTED]: valid = True
            
        # From EXECUTING
        elif self._state == AutonomyState.EXECUTING:
            if target_state in [AutonomyState.PAUSED, AutonomyState.ESCALATED, AutonomyState.COMPLETED, AutonomyState.ABORTED]: valid = True
            
        # From PAUSED
        elif self._state == AutonomyState.PAUSED:
            if target_state in [AutonomyState.EXECUTING, AutonomyState.ABORTED]: valid = True
            
        # From ESCALATED
        elif self._state == AutonomyState.ESCALATED:
            # User can Resume (EXECUTING) or Abort (ABORTED)
            if target_state in [AutonomyState.EXECUTING, AutonomyState.ABORTED]: valid = True
            
        # Terminal States (COMPLETED, ABORTED) can only go back to IDLE
        elif self._state in [AutonomyState.COMPLETED, AutonomyState.ABORTED]:
            if target_state == AutonomyState.IDLE: valid = True

        if not valid:
            raise InvalidTransitionError(f"Cannot transition from {self._state.name} to {target_state.name}")
            
        logger.info(f"Autonomy State: {self._state.name} -> {target_state.name}")
        self._state = target_state

autonomy_state_machine = AutonomyStateMachine()
