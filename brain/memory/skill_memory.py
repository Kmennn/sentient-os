
import logging
import json
import os
from typing import Dict, List, Optional
from dataclasses import asdict
from brain.skills.skill_abstraction import SkillData

logger = logging.getLogger(__name__)

class SkillMemory:
    """
    Persistent store for Learned Skills.
    """
    def __init__(self, storage_path="brain/data/skills.json"):
        self.storage_path = storage_path
        self.skills: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.storage_path):
            self.skills = {}
            return
            
        try:
            with open(self.storage_path, 'r') as f:
                self.skills = json.load(f)
            logger.info(f"SkillMemory: Loaded {len(self.skills)} skills.")
        except Exception as e:
            logger.error(f"Failed to load skills: {e}")
            self.skills = {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.skills, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save skills: {e}")

    def save_skill(self, skill: SkillData):
        data = asdict(skill)
        self.skills[skill.name] = data
        self._save()
        logger.info(f"SkillMemory: Saved '{skill.name}'.")

    def get_skill(self, name: str) -> Optional[SkillData]:
        data = self.skills.get(name)
        if not data:
            return None
        return SkillData(**data)
        
    def list_skills(self) -> List[str]:
        return list(self.skills.keys())

skill_memory = SkillMemory()
