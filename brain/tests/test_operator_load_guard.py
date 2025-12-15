
import pytest
import time
from brain.safety.operator_load_guard import OperatorLoadGuard

def test_flicker_locking():
    guard = OperatorLoadGuard()
    
    # 3 Switches quickly
    guard.record_switch()
    guard.record_switch()
    guard.record_switch()
    
    assert not guard.is_locked() # 3 is limit, need > 3
    
    guard.record_switch()
    assert guard.is_locked()

def test_window_expiry():
    guard = OperatorLoadGuard()
    guard._window_seconds = 0.1
    
    guard.record_switch()
    guard.record_switch()
    
    time.sleep(0.2)
    
    guard.record_switch() # Past ones should drift out
    assert not guard.is_locked()
