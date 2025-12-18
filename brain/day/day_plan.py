from dataclasses import dataclass, field
from typing import List, Dict, Any
from brain.routines.routine import Routine

@dataclass
class PlanItem:
    """
    Unified item for visualization (Routine, Task, Conflict).
    """
    id: str
    type: str # 'ROUTINE', 'TASK', 'DEFERRED', 'CONFLICT'
    name: str
    start_seconds: int 
    duration_seconds: int
    details: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

@dataclass
class DayPlan:
    """
    Snapshot of the day.
    """
    date_str: str # "YYYY-MM-DD"
    items: List[PlanItem] = field(default_factory=list)
    trust_level: str = "UNKNOWN"
    summary: str = ""
