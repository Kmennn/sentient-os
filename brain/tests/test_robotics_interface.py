
import pytest
from brain.robotics.robotics_interface import RoboticsInterface

def test_movement():
    bot = RoboticsInterface()
    target = (0.5, 0.5, 0.2)
    success = bot.move_to(target)
    assert success
    assert bot.position == target

def test_grasp_cycle():
    bot = RoboticsInterface()
    assert bot.gripper_state == "OPEN"
    
    bot.grasp()
    assert bot.gripper_state == "CLOSED"
    
    # Fail repeat grasp
    assert not bot.grasp() 
    
    bot.release()
    assert bot.gripper_state == "OPEN"
