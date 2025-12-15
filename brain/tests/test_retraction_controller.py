
import pytest
from brain.manipulation.recovery.retraction_controller import RetractionController
from brain.robotics.robot_controller import robot_controller

def test_retraction_logic(caplog):
    import logging
    caplog.set_level(logging.INFO)
    rc = RetractionController()
    
    # Mock robot state
    robot_controller.bridge.latest_pose = {"x": 0.5, "y": 0.5, "z": 0.1}
    # Mock connection
    robot_controller.bridge.connected = True
    robot_controller.bridge.is_mock = True

    # Trigger
    success = rc.trigger_retraction()
    
    assert success
    
    # Verify new pose (Mock updates instantly)
    new_pose = robot_controller.get_status()
    # Should be z=0.2 (0.1 + 0.1)
    assert abs(new_pose["z"] - 0.2) < 0.001
    assert "Retracting from" in caplog.text
