from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum
from brain.timeline.cognitive_event import CognitiveEvent
from brain.autonomy.autonomy_ledger import DecisionType

class RiskLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"

@dataclass
class CognitiveSummary:
    headline: str
    highlights: List[str]
    risk_level: RiskLevel
    agent_mix: Dict[str, float] # Agent -> Percentage

    def to_dict(self):
        return {
            "headline": self.headline,
            "highlights": self.highlights,
            "risk_level": self.risk_level.value,
            "agent_mix": self.agent_mix
        }

class CognitiveSummaryEngine:
    @staticmethod
    def summarize(events: List[CognitiveEvent]) -> CognitiveSummary:
        if not events:
            return CognitiveSummary(
                headline="System is idle.",
                highlights=[],
                risk_level=RiskLevel.NONE,
                agent_mix={"Observer": 0, "Analyst": 0, "Governor": 0, "System": 0}
            )
            
        # 1. Agent Mix
        counts = {"Observer": 0, "Analyst": 0, "Governor": 0, "System": 0}
        total = len(events)
        for e in events:
            role = e.agent if e.agent in counts else "System"
            counts[role] += 1
            
        mix = {k: round((v / total) * 100, 1) for k, v in counts.items()}
        
        # 2. Risk Level
        risk = RiskLevel.LOW
        has_adj = False
        has_conflict = False
        has_violation = False
        
        for e in events:
            typ = e.event_type
            # String check as raw decision type might be used or enum value
            # Assuming event_type matches AutonomyLedger strings or similar
            
            if "violation" in str(typ).lower():
                has_violation = True
            if "conflict" in str(typ).lower():
                has_conflict = True
            if "adjustment" in str(typ).lower():
                has_adj = True
                
        if has_violation:
            risk = RiskLevel.HIGH
        elif has_conflict or has_adj:
            risk = RiskLevel.MED
            
        # 3. Headline
        dominant = max(counts, key=counts.get)
        if risk == RiskLevel.HIGH:
            headline = f"System requires attention (Boundary Violation detected)."
        elif risk == RiskLevel.MED:
            headline = f"System is active with {dominant} adjustments and Sync resolution."
        else:
            headline = f"System is stable, operating primarily in {dominant} mode."
            
        # 4. Highlights (Top 3 distinct types)
        highlights = []
        # Group by summary or type
        unique_summaries = list(dict.fromkeys([e.summary for e in events]))
        if len(unique_summaries) > 3:
            highlights = unique_summaries[:3]
        else:
            highlights = unique_summaries
            
        return CognitiveSummary(
            headline=headline,
            highlights=highlights,
            risk_level=risk,
            agent_mix=mix
        )
