from brain.preferences.preference_store import PreferenceStore, ImportanceLevel
from brain.external.external_signal_classification import SignalRiskLevel

class AlertImportanceResolver:
    def __init__(self, preference_store: PreferenceStore):
        self.preference_store = preference_store
        
    def resolve(self, domain: str, risk_level: SignalRiskLevel) -> ImportanceLevel:
        # Rule 1: Critical Risk is always Critical Importance
        if risk_level == SignalRiskLevel.CRITICAL:
            return ImportanceLevel.CRITICAL
            
        # Rule 2: Explicit Preference or Inferred Meaning
        # preference_store.get_effective_preference handles both explicit and inferred.
        # It returns a dict with 'level' string.
        eff = self.preference_store.get_effective_preference(domain)
        level_str = eff.get("level", "medium")
        
        try:
            return ImportanceLevel(level_str)
        except:
            return ImportanceLevel.MEDIUM
