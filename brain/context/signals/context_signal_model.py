from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time

class ContextSource(Enum):
    APP_WINDOW = "app_window"
    CALENDAR = "calendar"
    SYSTEM_IDLE = "system_idle"

@dataclass
class ContextSignal:
    source: ContextSource
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self):
        return {
            "source": self.source.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "confidence": self.confidence
        }
