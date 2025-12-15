
import pytest
from brain.missions.escalation_engine import EscalationEngine, EscalationLevel
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, AutonomyState

def test_warning_escalation():
    sm = AutonomyStateMachine()
    engine = EscalationEngine(state_machine=sm)
    
    # Must be executing to escalate
    sm.transition(AutonomyState.PLANNING)
    sm.transition(AutonomyState.EXECUTING)
    
    engine.escalate("Low Confidence", EscalationLevel.WARNING)
    assert sm.state == AutonomyState.ESCALATED

def test_critical_abort():
    sm = AutonomyStateMachine()
    engine = EscalationEngine(state_machine=sm)
    
    sm.transition(AutonomyState.PLANNING)
    
    engine.escalate("Safety Breach", EscalationLevel.CRITICAL)
    assert sm.state == AutonomyState.ABORTED
