
import pytest
from brain.learning.blending_controller import BlendingController

def test_alpha_dominance():
    ctrl = BlendingController()
    # Alpha 1.0 -> Ignore Policy
    val = ctrl.compute_blend("lift_height", base_value=0.05, policy_delta=0.2, alpha=1.0)
    assert val == 0.05

def test_policy_influence():
    ctrl = BlendingController()
    # Alpha 0.5 -> Half Policy
    # Base 0.05, Delta 0.2. Final = 0.05 + 0.2 * 0.5 = 0.15
    val = ctrl.compute_blend("lift_height", base_value=0.05, policy_delta=0.2, alpha=0.5)
    assert abs(val - 0.15) < 0.001

def test_safety_fallback():
    ctrl = BlendingController()
    # Alpha 0.0 -> Full Policy.
    # Base 0.05, Delta 0.5 -> Final 0.55. Max is 0.3 (from default guard).
    val = ctrl.compute_blend("lift_height", base_value=0.05, policy_delta=0.5, alpha=0.0)
    # Should revert to base
    assert val == 0.05
