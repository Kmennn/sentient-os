
import pytest
from brain.safety.inter_step_verifier import InterStepVerifier
from brain.tasks.task_graph_builder import TaskNode
from brain.robotics.robot_controller import robot_controller

def test_grasp_verification():
    verifier = InterStepVerifier()
    
    # Mock Robot: Successful Grasp
    robot_controller.bridge.latest_pose = {"x":0, "gripper_state": "closed", "load_detected": True}
    robot_controller.bridge.connected = True
    
    node = TaskNode("1", "grasp", "cup", "grasp")
    assert verifier.verify_step_completion(node)

def test_grasp_fail():
    verifier = InterStepVerifier()
    
    # Mock Robot: Failed Grasp
    robot_controller.bridge.latest_pose = {"x":0, "gripper_state": "open"}
    
    node = TaskNode("1", "grasp", "cup", "grasp")
    assert not verifier.verify_step_completion(node)
