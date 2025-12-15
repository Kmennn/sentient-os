
import logging
from enum import Enum, auto
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, AutonomyState, autonomy_state_machine

logger = logging.getLogger(__name__)

class EscalationLevel(Enum):
    INFO = auto()     # Log, don't stop
    WARNING = auto()  # Pause, ask user
    CRITICAL = auto() # Abort

class EscalationEngine:
    """
    Decides the severity of an issue and triggers state transitions.
    """
    def __init__(self, state_machine: AutonomyStateMachine = autonomy_state_machine):
        self.sm = state_machine
        
    def escalate(self, reason: str, level: EscalationLevel):
        logger.warning(f"Escalation [{level.name}]: {reason}")
        
        if level == EscalationLevel.INFO:
            return # No action needed
            
        elif level == EscalationLevel.WARNING:
            # Transition to ESCALATED or PAUSED
            if self.sm.state == AutonomyState.EXECUTING:
                self.sm.transition(AutonomyState.ESCALATED)
                
        elif level == EscalationLevel.CRITICAL:
            # Immediate Abort
            if self.sm.state != AutonomyState.ABORTED:
                self.sm.transition(AutonomyState.ABORTED)

escalation_engine = EscalationEngine()
