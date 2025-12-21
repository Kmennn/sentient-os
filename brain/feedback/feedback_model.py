from enum import Enum
from dataclasses import dataclass, field
import time
from typing import Optional

class FeedbackType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class FeedbackSignal:
    type: FeedbackType
    target_id: str # macro_name, action_id, or "system_general"
    timestamp: float = field(default_factory=time.time)
    comment: Optional[str] = None
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "target_id": self.target_id,
            "timestamp": self.timestamp,
            "comment": self.comment
        }
