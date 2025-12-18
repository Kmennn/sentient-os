from dataclasses import dataclass, field
from typing import List, Dict, Any
from brain.day.day_plan import DayPlan

@dataclass
class WeeklyPattern:
    """
    Represents a detected pattern in the week.
    """
    type: str # 'HEAVY_LOAD', 'CONFLICT_PRONE', 'ROUTINE_HEAVY', 'FREE_DAY'
    description: str
    day_of_week: int = -1 # 0=Mon, 6=Sun, -1=General
    confidence: float = 1.0

@dataclass
class WeekPlan:
    """
    Snapshot of the week (7 days).
    """
    week_start_date: str # "YYYY-MM-DD"
    days: List[DayPlan] = field(default_factory=list)
    patterns: List[WeeklyPattern] = field(default_factory=list)
