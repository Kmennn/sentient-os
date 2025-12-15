
import logging
from brain.memory.skill_memory import skill_memory, SkillData

logger = logging.getLogger(__name__)

class SkillMigrationV1toV2:
    """
    Upgrades skills to v2.8 format (adding affordance requirements).
    """
    def run(self):
        logger.info("Starting Skill Migration (v1 -> v2)...")
        skills = skill_memory.list_skills()
        
        migrated_count = 0
        for name in skills:
            skill = skill_memory.get_skill(name)
            if not skill: continue
            
            updated = False
            # Check if required_affordance exists
            if "required_affordance" not in skill.metadata:
                skill.metadata["required_affordance"] = "use" # Default safe
                updated = True
                
            if updated:
                skill_memory.save_skill(skill)
                migrated_count += 1
                
        logger.info(f"Migration Complete. Updated {migrated_count} skills.")

skill_migration = SkillMigrationV1toV2()
