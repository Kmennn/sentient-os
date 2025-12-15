
import pytest
from brain.embodiment.motion_model import MotionModel

def test_stationary():
    mm = MotionModel()
    mm.update((0.0, 0.0, 9.8), (0,0,0))
    assert mm.state == "STATIONARY"
    assert mm.get_orientation() == "FLAT"

def test_moving():
    mm = MotionModel()
    # Shake it
    mm.update((0.0, 15.0, 5.0), (0,0,0))
    assert mm.state == "MOVING"
    
def test_orientation():
    mm = MotionModel()
    mm.update((0.0, 9.8, 0.0), (0,0,0))
    assert mm.get_orientation() == "PORTRAIT"
