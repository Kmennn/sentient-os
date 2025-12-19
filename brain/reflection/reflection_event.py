from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Dict, Optional

class ReflectionEventType(Enum):
    ALERT_FILTERED = "alert_filtered"
    ALERT_SHOWN = "alert_shown"
    ALERT_ACKED = "alert_acked"
    ALERT_DISMISSED = "alert_dismissed"
    USER_MANUAL_SEARCH = "user_manual_search"

@dataclass
class ReflectionEvent:
    event_type: ReflectionEventType
    domain: str
    item_id: Optional[str] = None # suggestion_id or similar
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict) # e.g., {'query': '...'}
