import json
import os
import time
from typing import Dict, List, Optional
from collections import deque

class TrustGate:
    """
    Manages Annoyance Budget and Trust Thresholds.
    Prevents spam and suppresses distrusted actions.
    """
    MAX_SUGGESTIONS_PER_HOUR = 3
    MAX_SUGGESTIONS_PER_DAY = 10
    
    def __init__(self, state_path="brain/autonomy/trust_state.json"):
        self.state_path = state_path
        self.suggestion_history: List[float] = [] # Timestamps
        self.feedback_score: Dict[str, int] = {} # target -> score
        self._load()

    def check_budget(self) -> bool:
        """Returns True if we are within the annoyance budget."""
        now = time.time()
        # Clean old
        self.suggestion_history = [t for t in self.suggestion_history if now - t < 86400]
        
        last_hour = [t for t in self.suggestion_history if now - t < 3600]
        
        if len(last_hour) >= self.MAX_SUGGESTIONS_PER_HOUR:
            return False
            
        if len(self.suggestion_history) >= self.MAX_SUGGESTIONS_PER_DAY:
            return False
            
        return True

    def consume_budget(self):
        self.suggestion_history.append(time.time())
        self._save()

    def record_feedback(self, target_id: str, is_positive: bool):
        current = self.feedback_score.get(target_id, 0)
        self.feedback_score[target_id] = current + (1 if is_positive else -2) # Negative weighs more
        self._save()

    def is_suppressed(self, target_id: str) -> bool:
        """Returns True if target has too much negative feedback."""
        return self.feedback_score.get(target_id, 0) <= -3

    def _save(self):
        try:
            data = {
                "history": self.suggestion_history,
                "scores": self.feedback_score
            }
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[TRUST] Save failed: {e}")

    def _load(self):
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r') as f:
                    data = json.load(f)
                    self.suggestion_history = data.get("history", [])
                    self.feedback_score = data.get("scores", {})
            except Exception:
                pass
