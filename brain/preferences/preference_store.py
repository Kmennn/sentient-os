import json
import os
import time
from typing import Dict, Optional, Union
from brain.preferences.explicit_preference import ExplicitPreference, ImportanceLevel
from brain.memory.meaning_memory import MeaningMemory

class PreferenceStore:
    def __init__(self, meaning_memory: MeaningMemory, persistence_path: str = "brain_data/user_preferences.json"):
        self.meaning_memory = meaning_memory
        self.persistence_path = persistence_path
        self._preferences: Dict[str, ExplicitPreference] = {} # domain -> ExplicitPreference
        self.min_display_threshold = ImportanceLevel.MEDIUM
        self._load()
        
    def _load(self):
        if not os.path.exists(self.persistence_path):
            return
            
        try:
            with open(self.persistence_path, "r") as f:
                data = json.load(f)
                
                # Load Threshold if exists
                if "min_display_threshold" in data:
                    try:
                        self.min_display_threshold = ImportanceLevel(data["min_display_threshold"])
                    except:
                        pass
                
                # Load Domains
                domains = data.get("domains", {})
                # Backward compatibility for flat structure if needed, but we just started v15.0 so flat is likely.
                # v15.0 saved {domain: dict}.
                # We need to migrate or handle both.
                # Let's check structure. v15.0 `_save` did: `data = {k: v.to_dict() ...}`
                # So if we want to add root fields, we need to change structure to `{"domains": {...}, "threshold": ...}`
                # Detection: if keys are domains or fixed keys.
                
                # Migration logic:
                if "domains" not in data and len(data) > 0 and "min_display_threshold" not in data:
                     # Old format (v15.0) - assume all keys are domains
                     domains = data
                elif "domains" in data:
                     domains = data["domains"]
                else:
                     domains = {} # Empty or new structure only
                
                for domain, d in domains.items():
                    d['importance_level'] = ImportanceLevel(d['importance_level'])
                    self._preferences[domain] = ExplicitPreference(**d)
                    
        except Exception as e:
            print(f"Error loading preferences: {e}")

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            # New Structure
            data = {
                "min_display_threshold": self.min_display_threshold.value,
                "domains": {k: v.to_dict() for k, v in self._preferences.items()}
            }
            with open(self.persistence_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
            
    def set_preference(self, domain: str, level: ImportanceLevel) -> ExplicitPreference:
        pref = ExplicitPreference(
            domain=domain,
            importance_level=level,
            updated_at=time.time()
        )
        self._preferences[domain] = pref
        self._save()
        return pref
        
    def get_explicit_preference(self, domain: str) -> Optional[ExplicitPreference]:
        return self._preferences.get(domain)
        
    def get_effective_preference(self, domain: str) -> Dict:
        """
        Reconciles explicit preference with learned meaning.
        Returns a dict describing the effective state.
        """
        # 1. Check Explicit
        if domain in self._preferences:
            pref = self._preferences[domain]
            return {
                "source": "EXPLICIT_USER",
                "level": pref.importance_level.value,
                "score": 1.0 # Override implies max weight
            }
            
        # 2. Check Meaning Fallback
        meaning_score = self.meaning_memory.get_relevance(domain)
        
        # Map score to level (Heuristic)
        level = "medium"
        if meaning_score < 0.3:
            level = "low"
        elif meaning_score < 0.7:
            level = "medium"
        elif meaning_score < 0.9:
            level = "high"
        else:
            level = "critical"
            
        return {
            "source": "INFERRED_MEANING",
            "level": level,
            "score": meaning_score
        }

    def get_all_explicit_preferences(self) -> Dict[str, ExplicitPreference]:
        return self._preferences.copy()
