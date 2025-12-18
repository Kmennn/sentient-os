from brain.external.external_signal import ExternalSignal
from brain.external.external_signal_classification import SignalRiskLevel

class EmergencyVisibilityPolicy:
    def check_visibility(self, signal: ExternalSignal) -> tuple[str, str]:
        """
        Determines the visibility level of a suggestion based on signal risk.
        Returns: (visibility_level, explanation)
        """
        if signal.risk_level == SignalRiskLevel.CRITICAL:
            return "FORCE_VISIBLE", f"Critical Signal: {signal.title}"
            
        return "NORMAL", ""
