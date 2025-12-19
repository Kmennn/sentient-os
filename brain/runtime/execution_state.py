from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import time

class ActionPhase(str, Enum):
    PLANNED = "PLANNED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"

@dataclass
class ExecutionState:
    active_action_id: Optional[str] = None
    action_phase: ActionPhase = ActionPhase.PLANNED
    started_at: float = 0.0
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    requires_human_reconfirm: bool = False
    error: Optional[str] = None
