
import pytest
from brain.skills.skill_replay_engine import SkillReplayEngine
from brain.skills.skill_abstraction import SkillData
from brain.memory.skill_memory import skill_memory
from brain.robotics.robot_controller import robot_controller

def test_replay_flow(caplog):
    sre = SkillReplayEngine()
    
    # Mock Skill
    skill = SkillData("safe_move", [{"t":0,"x":0,"y":0,"z":0}, {"t":1,"x":0.1,"y":0,"z":0}], {"duration":1})
    skill_memory.save_skill(skill)
    
    # Mock Robot
    robot_controller.bridge.latest_pose = {"x":0, "y":0, "z":0.2} # Safe start Z
    robot_controller.bridge.connected = True
    robot_controller.bridge.is_mock = True
    
    import logging
    caplog.set_level(logging.INFO)
    
    success = sre.replay_skill("safe_move")
    assert success
    assert "Executing" in caplog.text

def test_unsafe_replay(caplog):
    sre = SkillReplayEngine()
    
    # Skill moves DOWN 0.5m (unsafe if start z=0.2)
    skill = SkillData("crash_move", [{"t":0,"x":0,"y":0,"z":0}, {"t":1,"x":0,"y":0,"z":-0.5}], {"duration":1})
    skill_memory.save_skill(skill)
    
    robot_controller.bridge.latest_pose = {"x":0, "y":0, "z":0.2}
    
    success = sre.replay_skill("crash_move")
    assert not success
    assert "BLOCKED" in caplog.text
