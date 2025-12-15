
import pytest
import time
from brain.learning.alpha_ramp_controller import AlphaRampController

def test_smooth_transition():
    ctrl = AlphaRampController(start_alpha=1.0)
    ctrl.set_target(0.0)
    
    # Update immediately
    val = ctrl.update()
    assert val == 1.0 # Negligible time passed, or very small delta
    
    # Mock time passage by sleeping or manually setting last_update_time?
    # Better to inject time, but class uses time.time().
    # Let's mock time passage by calling update with delay simulation if we refactor,
    # or just sleep 0.1s for test.
    
    time.sleep(0.1)
    val = ctrl.update()
    # Max rate 0.5/s. 0.1s -> 0.05 change.
    # Should be approx 0.95
    assert val < 1.0
    assert val > 0.9

def test_force_override():
    ctrl = AlphaRampController(start_alpha=0.0)
    ctrl.force_override(1.0)
    assert ctrl.current_alpha == 1.0
