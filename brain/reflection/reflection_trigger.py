from typing import List, Optional
from brain.load.load_model import LoadSnapshot, LoadLevel
from brain.week.week_plan import WeekPlan, WeeklyPattern
from brain.reflection.reflection_prompt import ReflectionPrompt, PromptType
import uuid

class ReflectionTrigger:
    """
    Checks for patterns that warrant a reflection prompt.
    """
    
    def check_triggers(self, week_plan: WeekPlan, load_snapshots: List[LoadSnapshot]) -> Optional[ReflectionPrompt]:
        # 1. Check for High Load Streak (>= 2 days of HIGH load in the snapshots)
        # Snapshots are usually future or recent past?
        # Let's assume input snapshots cover the period of interest.
        
        high_load_streak = 0
        for snap in load_snapshots:
            if snap.level == LoadLevel.HIGH:
                high_load_streak += 1
            else:
                high_load_streak = 0
                
            if high_load_streak >= 2:
                return ReflectionPrompt(
                    prompt_id=str(uuid.uuid4()),
                    type=PromptType.LOAD,
                    pattern_description="Multiple consecutive days of high activity observed.",
                    confidence=0.9
                )
                
        # 2. Check for Conflict Patterns in Week Plan
        for pattern in week_plan.patterns:
            if pattern.type == "CONFLICT_PRONE":
                # Only trigger if confidence is high
                if pattern.confidence > 0.8:
                     return ReflectionPrompt(
                        prompt_id=str(uuid.uuid4()),
                        type=PromptType.CONFLICT,
                        pattern_description=pattern.description,
                        confidence=pattern.confidence
                    )
        
        return None
