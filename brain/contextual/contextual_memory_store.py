import json
import os
import time
from typing import List, Dict

class ContextualMemoryStore:
    def __init__(self, persistence_path: str = "brain_data/contextual_memory.jsonl"):
        self.persistence_path = persistence_path
        self._history: List[Dict] = []
        self._load()
        
    def _load(self):
        """Loads contextual history from disk."""
        if not os.path.exists(self.persistence_path):
            return
            
        try:
            with open(self.persistence_path, "r") as f:
                for line in f:
                    if line.strip():
                        self._history.append(json.loads(line))
        except Exception as e:
            print(f"Error loading contextual memory: {e}")
            
    def record_event(self, context_dict: Dict):
        """Records a narrated context event."""
        # Ensure timestamp
        if "recorded_at" not in context_dict:
            context_dict["recorded_at"] = time.time()
            
        self._history.append(context_dict)
        
        # Persist
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, "a") as f:
                f.write(json.dumps(context_dict) + "\n")
        except Exception as e:
            print(f"Error saving contextual memory: {e}")
            
    def get_history(self) -> List[Dict]:
        return self._history
