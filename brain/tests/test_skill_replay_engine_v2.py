
import pytest
import math
from brain.skills.skill_replay_engine_v2 import SkillReplayEngineV2
from brain.vision.object_semantics import object_registry, SemanticObject
from brain.skills.skill_abstraction import SkillData
from brain.memory.skill_memory import skill_memory
from brain.robotics.robot_controller import robot_controller

def test_semantic_replay(caplog):
    srv2 = SkillReplayEngineV2()
    
    # Setup: Skill
    skill = SkillData("push", [{"t":0,"x":0,"y":0,"z":0}, {"t":1,"x":0.5,"y":0,"z":0}], {"duration":5.0})
    skill_memory.save_skill(skill)
    
    # Setup: Object (Rotated 90 deg, Raised 0.1m)
    obj = SemanticObject("box", "box", "tool", {"x":1, "y":1, "z":0.1}, {"yaw": math.pi/2})
    object_registry.update_object(obj)
    
    # Mock Robot
    robot_controller.bridge.connected = True
    robot_controller.bridge.is_mock = True
    
    # Execute "use" (allowed for tool)
    import logging
    caplog.set_level(logging.INFO)
    
    success = srv2.replay_skill_on_object("push", "box", "use")
    print(caplog.text)
    assert success
    assert "Executing" in caplog.text

def test_forbidden_replay(caplog):
    srv2 = SkillReplayEngineV2()
    
    # Laptop
    obj = SemanticObject("macbook", "macbook", "electronics", {"x":0,"y":0,"z":0})
    object_registry.update_object(obj)
    
    # Skill (Pour)
    skill = SkillData("pour", [{"t":0,"x":0,"y":0,"z":0}], {"duration":1})
    skill_memory.save_skill(skill)
    
    # Try "pour_into" on electronics
    success = srv2.replay_skill_on_object("pour", "macbook", "pour_into")
    assert not success
    assert "Affordance Guard" in caplog.text
