from enum import StrEnum, auto
from dataclasses import dataclass
from typing import Optional

class InterruptWindowMode(StrEnum):
    ALLOW_ALL = auto()          # Allow all qualified interrupts (Logic applies)
    IMPORTANT_ONLY = auto()     # Only Deadline/UserDep
    SILENT = auto()             # Block all (Except Safety)

@dataclass
class InterruptWindow:
    start_time: str # "HH:MM" 24h
    end_time: str   # "HH:MM"
    mode: InterruptWindowMode
    name: str = "custom"
    
    def contains_time(self, time_str: str) -> bool:
        # Simple HH:MM comparison
        # Handle wrap around midnight? For MVP, assume start < end or simple day bounds.
        # If start > end (e.g. 23:00 to 07:00), we handle that logic.
        
        current = self._to_mins(time_str)
        start = self._to_mins(self.start_time)
        end = self._to_mins(self.end_time)
        
        if start <= end:
            return start <= current < end # Half-open interval [start, end)
        else:
            # Wraps midnight
            return current >= start or current < end

    def _to_mins(self, t_str: str) -> int:
        h, m = map(int, t_str.split(':'))
        return h * 60 + m

    def to_dict(self):
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "mode": self.mode.value,
            "name": self.name
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            start_time=data["start_time"],
            end_time=data["end_time"],
            mode=InterruptWindowMode(data.get("mode", "allow_all")),
            name=data.get("name", "custom")
        )
