from brain.external.external_signal import ExternalSignal
from brain.external.external_signal_classification import SignalRiskLevel
from brain.preferences.interrupt_style import InterruptStyle

class ExternalSuggestionPolicy:
    def should_allow_suggestion(self, signal: ExternalSignal, trust_score: float, focus_active: bool, presence_public: bool, interrupt_style: InterruptStyle) -> tuple[bool, str]:
        """
        Determines if an External Signal should trigger a User Suggestion.
        """
        # 1. Minimum Risk Level (Don't spam for Low/Med)
        if signal.risk_level not in [SignalRiskLevel.HIGH, SignalRiskLevel.CRITICAL]:
            return False, f"Risk too low ({signal.risk_level.value})"
            
        # 2. Minimum Confidence
        if signal.confidence < 0.8:
            return False, f"Confidence too low ({signal.confidence})"
            
        # 3. Minimum Trust (System Trust)
        if trust_score < 0.6:
            return False, f"Trust too low ({trust_score})"
            
        # 4. Context Gates
        if presence_public:
            return False, "User in Public"
            
        if focus_active:
            # Maybe allow Critical? For now, block all to be safe.
            if signal.risk_level == SignalRiskLevel.CRITICAL:
                pass # Allow Critical even in focus? 
                # User Requirement: "focus != ACTIVE" strict for now.
                return False, "Focus Active"
            else:
                return False, "Focus Active"
                
        if interrupt_style == InterruptStyle.NEVER_INTERRUPT:
            return False, "Do Not Disturb"
            
        return True, "Allowed"
