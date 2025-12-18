from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

class ChangeType(Enum):
    MOVE_TASK = auto()
    REMOVE_TASK = auto()
    # RESCHEDULE = auto() # Maybe confusing with move? Let's stick to simple "Move" for now.

@dataclass
class WhatIfScenario:
    """
    Represents a hypothetical change to the schedule.
    """
    scenario_id: str
    change_type: ChangeType
    target_item_id: str
    new_start_seconds: Optional[int] = None # For MOVE
