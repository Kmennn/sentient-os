from brain.autonomy.trust_model import TrustModel
from brain.preferences.scheduling_preferences import SchedulingPreferences

class DayPolicy:
    """
    Determines how the Day Plan is presented based on User Trust & Preferences.
    """
    
    def __init__(self, trust_model: TrustModel = None):
        self.trust_model = trust_model or TrustModel()
        
    def should_show_warnings(self, user_id: str) -> bool:
        """
        High trust users might want less noise? 
        Or low trust users need strictly shown conflicts?
        Actually, conflicts are always important.
        Maybe we hide 'minor' warnings for high trust?
        For v5.0, always show, but maybe vary verbosity.
        """
        return True

    def get_view_mode(self, user_id: str) -> str:
        """
        'DETAILED' vs 'SUMMARY'.
        """
        # score = self.trust_model.get_current_score()
        # For now, simplistic.
        return 'DETAILED'
