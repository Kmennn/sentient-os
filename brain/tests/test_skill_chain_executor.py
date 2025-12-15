
import pytest
from brain.skills.skill_chain_executor import SkillChainExecutor
from brain.tasks.task_graph_builder import TaskNode
from brain.vision.object_semantics import object_registry, SemanticObject
from brain.skills.skill_abstraction import SkillData
from brain.memory.skill_memory import skill_memory
from brain.robotics.robot_controller import robot_controller

def test_chain_success(caplog):
    # Setup
    executor = SkillChainExecutor()
    
    # 1. Register Object
    obj = SemanticObject("cup", "cup", "vessel", {"x": 1, "y": 0, "z": 0})
    object_registry.update_object(obj)
    
    # 2. Register Skill
    skill = SkillData("grasp", [{"t":0,"x":0,"y":0,"z":0}], {"duration":1})
    skill_memory.save_skill(skill)
    
    # 3. Mock Robot (Pass verification)
    robot_controller.bridge.latest_pose = {"x":0, "gripper_state": "closed", "load_detected": True}
    robot_controller.bridge.connected = True
    
    # Chain
    node1 = TaskNode("1", "grasp", "cup", "grasp")
    chain = [node1]
    
    import logging
    caplog.set_level(logging.INFO)
    
    success = executor.execute_chain(chain)
    
    # Debug info
    if not success:
         print(caplog.text)
         
    assert success
    assert "Chain Execution Completed" in caplog.text

def test_chain_occlusion_fail(caplog):
    executor = SkillChainExecutor()
    
    # Block path
    executor.planner.add_obstacle(executor.planner._from_grid((5,0,0)), radius=1.0) # Block near target?
    # Actually, planner resolution 0.05. (1,0,0) is grid (20,0,0).
    # Current pos (0,0,0).
    # Let's block (0.5, 0, 0).
    from brain.manipulation.manipulator_v2 import Point3D
    executor.planner.add_obstacle(Point3D(0.5, 0, 0), radius=0.2)
    
    obj = SemanticObject("cup", "cup", "vessel", {"x": 1, "y": 0, "z": 0})
    object_registry.update_object(obj)
    
    node = TaskNode("2", "lift", "cup", "move")
    chain = [node]
    
    success = executor.execute_chain(chain)
    assert not success
    assert "Path blocked" in caplog.text
