
import pytest
from brain.robotics.execution_mode import ExecutionModeManager, Mode

def test_mode_switching():
    em = ExecutionModeManager()
    assert em.get_mode() == Mode.SIMULATION
    
    em.set_mode("DRY_RUN")
    assert em.get_mode() == Mode.DRY_RUN
    
    em.set_mode("LIVE")
    assert em.get_mode() == Mode.LIVE

def test_estop_behavior():
    em = ExecutionModeManager()
    em.set_mode("LIVE")
    
    em.trigger_estop()
    assert em.is_estop_active
    assert em.get_mode() == Mode.SIMULATION # Should revert
    
    # Try setting mode while Estop
    success = em.set_mode("LIVE")
    assert not success

def test_validate_action():
    em = ExecutionModeManager()
    em.trigger_estop()
    assert not em.validate_action()
    
    em.clear_estop()
    assert em.validate_action()
