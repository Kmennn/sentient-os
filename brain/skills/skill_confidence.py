
import logging
from dataclasses import dataclass
from typing import Dict

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceData:
    success_count: int = 0
    fail_count: int = 0
    
    @property
    def score(self) -> float:
        total = self.success_count + self.fail_count
        if total == 0: return 0.5 # Neutral start
        return self.success_count / total

class SkillConfidenceManager:
    """
    Manages trust levels for learned skills.
    """
    def __init__(self):
        self.scores: Dict[str, ConfidenceData] = {}
        
    def record_execution(self, skill_name: str, success: bool):
        if skill_name not in self.scores:
            self.scores[skill_name] = ConfidenceData()
            
        if success:
            self.scores[skill_name].success_count += 1
        else:
            self.scores[skill_name].fail_count += 1
            
        logger.info(f"Confidence Updated for '{skill_name}': {self.scores[skill_name].score:.2f}")

    def is_viable(self, skill_name: str) -> bool:
        if skill_name not in self.scores:
            return True # Allow trial
            
        return self.scores[skill_name].score > 0.4 # Minimum threshold

skill_confidence = SkillConfidenceManager()
