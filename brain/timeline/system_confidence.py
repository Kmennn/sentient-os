from dataclasses import dataclass, field
from enum import Enum
from typing import List
import time
from brain.timeline.cognitive_event import CognitiveEvent
from brain.timeline.cognitive_summary import RiskLevel

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class SystemConfidence:
    level: ConfidenceLevel
    reason: str
    since: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "level": self.level.value,
            "reason": self.reason,
            "since": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.since))
        }

class ConfidenceEngine:
    @staticmethod
    def evaluate(events: List[CognitiveEvent], last_confidence: 'SystemConfidence' = None) -> SystemConfidence:
        # Determine based on risk logic similar to Summary
        # But focuses on "Assurance"
        
        has_violation = False
        has_conflict = False
        has_critical_filter = False
        recent_reflection_negative = False
        
        for e in events:
            txt = e.summary.lower()
            typ = e.event_type.lower()
            
            if "violation" in typ:
                has_violation = True
            if "conflict" in typ:
                has_conflict = True
            if "negative" in typ and "reflection" in typ:
                recent_reflection_negative = True
                
        level = ConfidenceLevel.HIGH
        reason = "System is operating normally. No critical events encountered."
        
        if has_violation:
            level = ConfidenceLevel.LOW
            reason = "Boundary violation detected. Assurance compromised."
        elif has_conflict:
            level = ConfidenceLevel.LOW
            reason = "Sync conflicts detected. Consistency check required."
        elif recent_reflection_negative:
            level = ConfidenceLevel.MEDIUM
            reason = "Self-correction in progress based on reflections."
            
        # Stability check: if level matches last level, keep 'since' timestamp
        if last_confidence and last_confidence.level == level:
            return SystemConfidence(level=level, reason=reason, since=last_confidence.since)
            
        return SystemConfidence(level=level, reason=reason)
