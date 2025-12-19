import json
import os
import time
from typing import Dict, List, Optional
from enum import Enum
from brain.memory.user_meaning import UserMeaning

class InteractionType(Enum):
    ACK = "ack"
    DISMISS = "dismiss"
    VIEW = "view"

class MeaningMemory:
    def __init__(self, persistence_path: str = "brain_data/user_meaning_v1.json"):
        self.persistence_path = persistence_path
        self._meanings: Dict[str, UserMeaning] = {} # domain -> UserMeaning
        self._load()
        
    def _load(self):
        if not os.path.exists(self.persistence_path):
            return
        
        try:
            with open(self.persistence_path, "r") as f:
                data = json.load(f)
                for domain, d in data.items():
                    self._meanings[domain] = UserMeaning(**d)
        except Exception as e:
            print(f"Error loading meaning memory: {e}")
            
    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            data = {k: v.to_dict() for k, v in self._meanings.items()}
            with open(self.persistence_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving meaning memory: {e}")

    def record_interaction(self, domain: str, interaction_type: InteractionType) -> float:
        """
        Updates relevance score for domain based on interaction.
        Returns the new score.
        """
        if domain not in self._meanings:
            self._meanings[domain] = UserMeaning(signal_domain=domain)
            
        entry = self._meanings[domain]
        entry.interaction_count += 1
        entry.last_interaction_ts = time.time()
        
        # Simple heuristic updates
        # ACK: High positive signal (+0.1)
        # VIEW: Light positive signal (+0.05)
        # DISMISS: Negative signal (-0.1)
        
        delta = 0.0
        if interaction_type == InteractionType.ACK:
            delta = 0.1
        elif interaction_type == InteractionType.VIEW:
            delta = 0.05
        elif interaction_type == InteractionType.DISMISS:
            delta = -0.1
            
        # Clamp 0.0 to 1.0
        entry.relevance_score = max(0.0, min(1.0, entry.relevance_score + delta))
        
        self._save()
        return entry.relevance_score
        
    def get_relevance(self, domain: str) -> float:
        if domain in self._meanings:
            return self._meanings[domain].relevance_score
        return 0.5 # Default neutral

    def get_all_meanings(self) -> List[Dict]:
        return [v.to_dict() for v in self._meanings.values()]
