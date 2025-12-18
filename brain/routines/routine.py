from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class Routine:
    name: str # e.g. "Morning Login"
    time_of_day_seconds: int # Seconds from midnight (approx start time)
    duration_seconds: int # Approx duration
    days_of_week: List[int] # 0=Monday, 6=Sunday
    confidence: float = 0.0 # 0.0 to 1.0
    protected: bool = False
    routine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def matches_time(self, current_seconds_from_midnight: int, tolerance: int = 1800) -> bool:
        """
        Does the current time fall roughly within this routine's start window?
        """
        diff = abs(current_seconds_from_midnight - self.time_of_day_seconds)
        return diff <= tolerance
