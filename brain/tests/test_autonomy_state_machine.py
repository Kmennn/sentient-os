
import pytest
from brain.autonomy.autonomy_state_machine import AutonomyStateMachine, AutonomyState, InvalidTransitionError

def test_valid_flow():
    sm = AutonomyStateMachine()
    sm.transition(AutonomyState.PLANNING)
    sm.transition(AutonomyState.EXECUTING)
    sm.transition(AutonomyState.COMPLETED)
    sm.transition(AutonomyState.IDLE)
    assert sm.state == AutonomyState.IDLE

def test_invalid_transition():
    sm = AutonomyStateMachine()
    # IDLE -> COMPLETED is invalid (must execute first)
    with pytest.raises(InvalidTransitionError):
        sm.transition(AutonomyState.COMPLETED)

def test_interruption():
    sm = AutonomyStateMachine()
    sm.transition(AutonomyState.PLANNING)
    sm.transition(AutonomyState.ABORTED) # Abort during planning is valid
    assert sm.state == AutonomyState.ABORTED
