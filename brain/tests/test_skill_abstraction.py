
import pytest
from brain.skills.skill_abstraction import SkillAbstraction
from brain.skills.demonstration_recorder import DemoPoint

def test_normalization():
    sa = SkillAbstraction()
    
    # Raw points: (1,1,1) -> (2,2,2)
    p1 = DemoPoint(100.0, 1.0, 1.0, 1.0, "")
    p2 = DemoPoint(101.0, 2.0, 2.0, 2.0, "")
    
    skill = sa.abstract([p1, p2], "test_skill")
    
    assert len(skill.points) > 0
    # First point should be (0,0,0) at t=0
    assert skill.points[0]["x"] == 0.0
    assert skill.points[0]["y"] == 0.0
    assert skill.points[0]["z"] == 0.0
    assert skill.points[0]["t"] == 0.0
    
    # Second should be (1,1,1) at t=1.0
    # Note: Decimation might keep it or not.
    # [::2] of 2 items is [item0]. If end appended: [item0, item1].
    assert skill.points[-1]["x"] == 1.0
    assert skill.points[-1]["t"] == 1.0

def test_metadata():
    sa = SkillAbstraction()
    p1 = DemoPoint(0,0,0,0,"")
    p2 = DemoPoint(1,1,0,0,"") # Move 1m in 1s = 1m/s
    
    skill = sa.abstract([p1, p2])
    assert abs(skill.metadata["max_speed"] - 1.0) < 0.001
