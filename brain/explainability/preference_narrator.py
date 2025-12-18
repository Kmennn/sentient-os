from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance
from brain.intents.deferral_engine import DeferralDecision, DeferralStrategy
from brain.explainability.time_narrator import TimeNarrator

class PreferenceNarrator:
    """
    Explains decisions with preference context.
    """
    def __init__(self):
        self.time_narrator = TimeNarrator()
        
    def explain(self, intent_desc: str, decision: DeferralDecision, prefs: SchedulingPreferences) -> str:
        base_msg = self.time_narrator.explain_deferral(intent_desc, decision)
        
        # Add preference context
        if decision.strategy == DeferralStrategy.EXPIRE or decision.strategy == DeferralStrategy.NONE:
            if prefs.delay_tolerance == DelayTolerance.LOW and "LOW tolerance" in decision.reason:
                return f"{base_msg} (Prevented delay due to your Preference: Low Tolerance)."
        
        if decision.strategy == DeferralStrategy.DELAY:
            if prefs.delay_tolerance == DelayTolerance.HIGH:
                return f"{base_msg} (Allowed by your Preference: High Tolerance)."
                
        return base_msg
