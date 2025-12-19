from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class RecoveryLevel(str, Enum):
    NONE = "NONE"
    SOFT = "SOFT"
    HARD = "HARD"

class RecoveryTrigger(str, Enum):
    FAILURE = "FAILURE"
    ROLLBACK = "ROLLBACK"
    BUDGET_PRESSURE = "BUDGET_PRESSURE"
    MANUAL = "MANUAL"

@dataclass
class RecoveryState:
    level: RecoveryLevel = RecoveryLevel.NONE
    triggered_by: Optional[RecoveryTrigger] = None
    cooldown_until: float = 0.0
    reason: str = ""
    
    def is_active(self, current_time: float) -> bool:
        return self.level != RecoveryLevel.NONE and current_time < self.cooldown_until
