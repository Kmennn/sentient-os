from dataclasses import dataclass
import time
from enum import Enum, auto

class InsightType(Enum):
    FOCUS_PATTERN = "focus_pattern"
    SCHEDULE_PRESSURE = "schedule_pressure"
    HABIT_DETECTED = "habit_detected"
    IDLE_OPPORTUNITY = "idle_opportunity"

@dataclass
class AmbientInsight:
    id: str
    type: InsightType
    description: str
    confidence: float
    created_at: float = time.time()
    is_private: bool = False
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "is_private": self.is_private
        }
