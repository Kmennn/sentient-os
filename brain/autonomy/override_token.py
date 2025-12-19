from dataclasses import dataclass
from enum import Enum
import time

class OverrideScope(str, Enum):
    ACTION = "ACTION"
    RECOVERY = "RECOVERY"
    BUDGET = "BUDGET"
    ALL = "ALL"

@dataclass
class OverrideToken:
    override_id: str
    requested_by: str
    reason: str
    scope: OverrideScope
    issued_at: float
    expires_at: float
    used: bool = False
    
    def is_valid(self) -> bool:
        return not self.used and time.time() < self.expires_at
