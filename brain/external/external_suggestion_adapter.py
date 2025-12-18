import uuid
from brain.external.external_signal import ExternalSignal
from brain.proactive.proactive_suggestion import ProactiveSuggestion, SuggestionType, SuggestionStatus

class ExternalSuggestionAdapter:
    def to_suggestion(self, signal: ExternalSignal) -> ProactiveSuggestion:
        """
        Converts an ExternalSignal into a ProactiveSuggestion.
        """
        return ProactiveSuggestion(
            suggestion_id=str(uuid.uuid4()),
            source_insight_id=signal.signal_id, # Link back to signal
            type=SuggestionType.EXTERNAL_SIGNAL,
            message=f"External Alert: {signal.title}",
            confidence=signal.confidence,
            action_id=None, # Safety: No actions for now
            status=SuggestionStatus.PENDING
        )
