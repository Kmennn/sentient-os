
import pytest
import time
from brain.skills.demonstration_recorder import DemonstrationRecorder
from brain.robotics.robot_controller import robot_controller

def test_recording_flow():
    rec = DemonstrationRecorder()
    
    # Mock Robot
    robot_controller.bridge.latest_pose = {"x": 1.0, "y": 2.0, "z": 3.0}
    robot_controller.bridge.connected = True
    robot_controller.bridge.is_mock = True

    rec.start_recording()
    time.sleep(0.25) # Should capture ~2-3 points (10Hz)
    points = rec.stop_recording()
    
    assert len(points) >= 2
    assert points[0].x == 1.0
    assert points[0].y == 2.0
    assert points[0].z == 3.0

def test_no_double_start(caplog):
    rec = DemonstrationRecorder()
    rec.start_recording()
    rec.start_recording()
    rec.stop_recording()
    
    assert "Recorder already active" in caplog.text
