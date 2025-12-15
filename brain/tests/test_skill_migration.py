
import pytest
from brain.migrations.skill_v1_to_v2 import SkillMigrationV1toV2
from brain.memory.skill_memory import skill_memory, SkillData

def test_migration():
    # Setup legacy skill
    legacy = SkillData("legacy_skill", [], {"duration": 1.0})
    skill_memory.save_skill(legacy)
    
    migrator = SkillMigrationV1toV2()
    migrator.run()
    
    # Check update
    updated = skill_memory.get_skill("legacy_skill")
    assert "required_affordance" in updated.metadata
    assert updated.metadata["required_affordance"] == "use"
