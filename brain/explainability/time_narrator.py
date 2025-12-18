import time
from brain.intents.deferral_engine import DeferralDecision, DeferralStrategy

class TimeNarrator:
    """
    Explains temporal events like deferrals or expirations.
    """
    
    def explain_deferral(self, intent_description: str, decision: DeferralDecision) -> str:
        if decision.strategy == DeferralStrategy.DELAY:
            delay_sec = int(decision.new_start_time - time.time())
            delay_min = round(delay_sec / 60, 1)
            return f"Mission '{intent_description}' delayed by {delay_min} mins. Reason: {decision.reason}."
            
        elif decision.strategy == DeferralStrategy.EXPIRE:
            return f"Mission '{intent_description}' EXPIRED. Reason: {decision.reason}."
            
        elif decision.strategy == DeferralStrategy.RESCHEDULE:
             return f"Mission '{intent_description}' rescheduled. Reason: {decision.reason}."
             
        return f"Mission '{intent_description}' rejected (No deferral possible)."
