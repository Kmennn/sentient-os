from dataclasses import dataclass
import time
from typing import Dict, Optional, List
from brain.memory.contextual_memory import ContextualMemory

@dataclass
class PatternInsight:
    count: int
    trend: str # stable, rising, falling
    last_seen: float
    confidence: float

class ContextualPatternAnalyzer:
    def __init__(self, memory: ContextualMemory):
        self.memory = memory
        
    def analyze_pattern(self, signal_title: str) -> PatternInsight:
        """
        Analyzes patterns for a given signal title.
        """
        freq = self.memory.summarize_frequency(signal_title)
        total = freq["total"]
        c7 = freq["7d"]
        c30 = freq["30d"]
        
        # Trend Logic
        trend = "stable"
        if c7 == 0 and total == 0:
            trend = "new"
        elif c7 > (c30 / 4) * 1.5:
             trend = "rising"
        elif c7 < (c30 / 4) * 0.5 and total > 5:
             trend = "falling"
             
        # Find last seen
        matches = [e for e in self.memory._history if e.get("title") == signal_title]
        last_seen = matches[-1]["generated_at"] if matches else time.time()
        
        return PatternInsight(
            count=total,
            trend=trend,
            last_seen=last_seen,
            confidence=0.9 if total > 2 else 0.5
        )
