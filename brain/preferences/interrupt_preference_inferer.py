from typing import List
from brain.intents.interrupt_reason import InterruptReason
from brain.preferences.interrupt_preferences import InterruptPreference, PreferenceBias

class InterruptPreferenceInferer:
    """
    Infers user preference bias based on historical outcomes.
    """
    
    def infer(self, reason: InterruptReason, history: List[bool]) -> InterruptPreference:
        if not history:
            return InterruptPreference(reason, 0.0, PreferenceBias.NEUTRAL, 0)
            
        wins = sum(1 for x in history if x)
        total = len(history)
        rate = wins / total
        
        bias = PreferenceBias.NEUTRAL
        if total >= 3: # Min sample size to form an opinion
            if rate >= 0.7:
                bias = PreferenceBias.LIKELY_ACCEPT
            elif rate <= 0.3:
                bias = PreferenceBias.LIKELY_REJECT
                
        return InterruptPreference(reason, rate, bias, total)
