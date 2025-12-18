from brain.autonomy.trust_model import TrustModel
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance

class ProactivePolicy:
    """
    Determines how aggressive proactive suggestions should be.
    """
    
    def can_suggest(self, user_id: str, trust_model: TrustModel, prefs: SchedulingPreferences) -> bool:
        """
        Check if user trust/prefs allow suggestions.
        """
        # If user explicitly turned off preemption (using it as a proxy for 'do not disturb' in v4.7?)
        # Or checking tolerance.
        
        # Hard check: If Trust < X, maybe don't suggest?
        # For now, MVP: Allow if Trust > 0.
        score = trust_model.get_effective_score(user_id)
        if score < 0.2:
            return False
            
        return True
        
    def get_suggestion_style(self, user_id: str, prefs: SchedulingPreferences) -> str:
        """
        Returns 'PASSIVE', 'NORMAL', 'ASSERTIVE'
        """
        if prefs.delay_tolerance == DelayTolerance.HIGH:
             return 'PASSIVE' # User is chill, don't nag.
        elif prefs.delay_tolerance == DelayTolerance.LOW:
             return 'ASSERTIVE' # User hates delays, suggest early so they don't wait.
        return 'NORMAL'
