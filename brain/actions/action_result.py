from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ActionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

@dataclass
class ActionResult:
    action_id: str
    status: ActionStatus
    reversible: bool
    revert_action_id: Optional[str] = None
    error_reason: Optional[str] = None

    def to_dict(self):
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "reversible": self.reversible,
            "revert_action_id": self.revert_action_id,
            "error_reason": self.error_reason
        }
