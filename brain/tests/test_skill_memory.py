
import pytest
import os
from brain.memory.skill_memory import SkillMemory
from brain.skills.skill_abstraction import SkillData

def test_persistence(tmp_path):
    # Use tmp file
    f = tmp_path / "skills.json"
    mem = SkillMemory(str(f))
    
    skill = SkillData("unit_test", [{"x":1}], {})
    mem.save_skill(skill)
    
    # Reload
    mem2 = SkillMemory(str(f))
    loaded = mem2.get_skill("unit_test")
    
    assert loaded is not None
    assert loaded.name == "unit_test"
    assert loaded.points[0]["x"] == 1

def test_missing_skill():
    mem = SkillMemory("dummy.json")
    assert mem.get_skill("non_existent") is None
