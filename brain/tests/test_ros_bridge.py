
import pytest
from brain.robotics.ros_bridge import RosBridge
from brain.robotics.robot_controller import RobotController

def test_bridge_init():
    rb = RosBridge()
    assert rb is not None
    # Assuming mock
    if rb.is_mock:
        assert rb.connected

def test_controller_move():
    rc = RobotController()
    success = rc.reach_to(0.5, 0.2, 0.1)
    assert success
    
    # In mock mode, pose updates instantly
    if rc.bridge.is_mock:
        pose = rc.get_status()
        assert pose["x"] == 0.5

def test_controller_grasp():
    rc = RobotController()
    assert rc.grasp_object()
    assert rc.release_object()
