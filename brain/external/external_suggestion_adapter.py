import uuid
from brain.external.external_signal import ExternalSignal
from brain.proactive.proactive_suggestion import ProactiveSuggestion, SuggestionType, SuggestionStatus

class ExternalSuggestionAdapter:
    def to_suggestion(self, signal: ExternalSignal) -> ProactiveSuggestion:
        """
        Converts an ExternalSignal into a ProactiveSuggestion.
        """
        # Assuming vis_level and vis_reason are defined or derived elsewhere in a real scenario
        # For this exercise, we'll assume they are available in this scope.
        # If they are meant to be attributes of signal, they should be accessed as such.
        # As per the instruction, they are directly used.
        from brain.proactive.proactive_suggestion import VisibilityLevel
        vis_level = VisibilityLevel.NORMAL
        vis_reason = "Default"

        return ProactiveSuggestion(
            suggestion_id=f"suggestion_{signal.signal_id}",
            source_insight_id=signal.signal_id,
            type=SuggestionType.EXTERNAL_SIGNAL,
            message=f"External Alert: {signal.title}",
            confidence=signal.confidence,
            visibility_level=vis_level,
            visibility_explanation=vis_reason,
            metadata={
                "domain": signal.domain.value,
                "risk_level": signal.risk_level.value
            },
            status=SuggestionStatus.PENDING
        )
