from enum import StrEnum, auto
from dataclasses import dataclass
import time

class InteractionType(StrEnum):
    FOCUS = auto() # App in foreground
    INPUT = auto() # Keyboard/Mouse/Touch
    VIEW = auto()  # Passive viewing
    PING = auto()  # Explicit "I'm here"

@dataclass
class ActiveDevice:
    device_id: str
    last_interaction_ts: float
    interaction_type: InteractionType
    confidence: float # 0.0 to 1.0 (calculated dynamically usually)
    
    @property
    def age(self):
        return time.time() - self.last_interaction_ts
