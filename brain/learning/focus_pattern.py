from enum import StrEnum, auto
from dataclasses import dataclass, field
from typing import List

class FocusPatternStatus(StrEnum):
    CANDIDATE = auto() # Detected, not yet proposed (low confidence)
    PROPOSED = auto()  # High confidence, waiting for user
    APPROVED = auto()  # User accepted -> Copied to Schedule
    REJECTED = auto()  # User blocked

@dataclass
class FocusPattern:
    pattern_id: str
    start_time: str # "HH:MM"
    end_time: str
    days: List[int] # 0=Mon, 6=Sun
    confidence: float = 0.0
    status: FocusPatternStatus = FocusPatternStatus.CANDIDATE
    source: str = "manual_focus"
    
    occurrence_count: int = 1
    
    def to_dict(self):
        return {
            "pattern_id": self.pattern_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "days": self.days,
            "confidence": self.confidence,
            "status": self.status.value,
            "source": self.source,
            "occurrence_count": self.occurrence_count
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            pattern_id=data["pattern_id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            days=data["days"],
            confidence=data.get("confidence", 0.0),
            status=FocusPatternStatus(data.get("status", "candidate")),
            source=data.get("source", "manual_focus"),
            occurrence_count=data.get("occurrence_count", 1)
        )
