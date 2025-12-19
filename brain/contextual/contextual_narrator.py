from typing import Dict, Optional
from brain.contextual.search_result import SearchResult
from brain.contextual.narrated_context import NarratedContext

class ContextualNarrator:
    def __init__(self):
        self._narrations: Dict[str, NarratedContext] = {} # signal_id -> narration
        
    def narrate(self, search_result: SearchResult) -> NarratedContext:
        """
        Converts a SearchResult into a neutral, human-readable narration.
        """
        # Logic to generate neutral text based on summary and confidence.
        # Strict Tone: Neutral, No Advice, No Fear.
        
        base_text = "Analysis of external sources indicates "
        if search_result.confidence_score > 0.8:
            base_text += "a high probability that "
        elif search_result.confidence_score > 0.5:
            base_text += "a possibility that "
        else:
            base_text += "uncertainty regarding whether "
            
        # Simplified extraction for this version
        explanation = f"{base_text}this event relates to {search_result.summary.split('.')[0].lower()}. Information was aggregated from {len(search_result.sources)} sources. No automated actions have been taken."
        
        narration = NarratedContext(
            signal_id=search_result.signal_id,
            summary_text=explanation,
            confidence_level=search_result.confidence_score,
            source_count=len(search_result.sources)
        )
        
        self._narrations[search_result.signal_id] = narration
        return narration
        
    def get_narration(self, signal_id: str) -> Optional[NarratedContext]:
        return self._narrations.get(signal_id)
