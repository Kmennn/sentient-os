from dataclasses import dataclass, field
import time
from typing import Dict
from enum import Enum

class SuggestionType(Enum):
    IDLE_OPPORTUNITY = "idle_opportunity"
    SCHEDULE_PRESSURE = "schedule_pressure"
    HABIT_DETECTED = "habit_detected"
    EXTERNAL_SIGNAL = "external_signal"

class SuggestionStatus(Enum):
    PENDING = "pending"
    DISMISSED = "dismissed"
    ACCEPTED = "accepted"
    AUTO_EXECUTED = "auto_executed"

class VisibilityLevel(Enum):
    NORMAL = "normal"
    FORCE_VISIBLE = "force_visible"

@dataclass
class ProactiveSuggestion:
    suggestion_id: str
    source_insight_id: str
    type: SuggestionType
    message: str
    confidence: float
    action_id: str = None # Optional link to executable action
    created_at: float = time.time()
    status: SuggestionStatus = SuggestionStatus.PENDING
    
    # v12.2 Visibility
    visibility_level: VisibilityLevel = VisibilityLevel.NORMAL
    visibility_explanation: str = ""
    
    # v15.1 Store extra context (domain, risk_level)
    metadata: Dict = field(default_factory=dict)
    
    # v15.1 Filtering
    is_filtered: bool = False
    filtered_reason: str = None
    
    def to_dict(self):
        return {
            "suggestion_id": self.suggestion_id,
            "source_insight_id": self.source_insight_id,
            "type": self.type.value,
            "message": self.message,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "status": self.status.value,
            "action_id": self.action_id,
            "visibility_level": self.visibility_level.value,
            "visibility_explanation": self.visibility_explanation,
            "metadata": self.metadata,
            "is_filtered": self.is_filtered,
            "filtered_reason": self.filtered_reason
        }
