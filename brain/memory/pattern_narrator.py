from dataclasses import dataclass
from brain.memory.contextual_pattern_analyzer import PatternInsight

@dataclass
class PatternExplanation:
    summary_text: str
    confidence: float
    last_seen: float
    trend_label: str
    
    def to_dict(self):
        return {
            "summary_text": self.summary_text,
            "confidence": self.confidence,
            "last_seen": self.last_seen,
            "trend_label": self.trend_label
        }

class PatternNarrator:
    def __init__(self):
        self._explanations = {} # signal_type -> PatternExplanation
        
    def explain(self, insight: PatternInsight, signal_type: str) -> PatternExplanation:
        """
        Generates a neutral explanation for the detected pattern.
        """
        text = ""
        if insight.trend == "new":
            text = f"This is the first detected occurrence of '{signal_type}' in the memory window."
        elif insight.trend == "rising":
            text = f"The frequency of '{signal_type}' is increasing. It has occurred {insight.count} times, with a concentration in the last 7 days."
        elif insight.trend == "falling":
            text = f"The frequency of '{signal_type}' is decreasing compared to the 30-day average."
        elif insight.trend == "stable":
            text = f"This pattern appears stable with {insight.count} total occurrences."
            
        explanation = PatternExplanation(
            summary_text=text,
            confidence=insight.confidence,
            last_seen=insight.last_seen,
            trend_label=insight.trend
        )
        
        self._explanations[signal_type] = explanation
        return explanation
        
    def get_explanation(self, signal_type: str):
        return self._explanations.get(signal_type)
