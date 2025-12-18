import time
from brain.intents.deferral_engine import DeferralEngine, DeferralDecision, DeferralStrategy
from brain.intents.conflict_detector import ConflictReport
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance

class PreferenceResolver:
    """
    Adjusts deferral decisions based on user preferences.
    """
    def __init__(self):
        self.engine = DeferralEngine()

    def resolve(self, report: ConflictReport, prefs: SchedulingPreferences) -> DeferralDecision:
        base_decision = self.engine.evaluate(report)
        
        # If engine says EXPIRE/NONE, preferences usually can't save it (physics/time constraints).
        if base_decision.strategy in [DeferralStrategy.EXPIRE, DeferralStrategy.NONE]:
            return base_decision
            
        # If engine says DELAY
        if base_decision.strategy == DeferralStrategy.DELAY:
            # Check duration
            delay_sec = base_decision.new_start_time - time.time()
            
            # LOW tolerance: Reject delays > 1 min
            if prefs.delay_tolerance == DelayTolerance.LOW:
                if delay_sec > 60:
                    return DeferralDecision(
                        DeferralStrategy.EXPIRE, 
                        reason="Delay exceeded LOW tolerance"
                    )
            
            # MEDIUM tolerance: Accept default (e.g. 5 min is fine).
            # HIGH tolerance: Accept default.
            
            return base_decision
            
        return base_decision
