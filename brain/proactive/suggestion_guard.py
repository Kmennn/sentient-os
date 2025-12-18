from dataclasses import dataclass, field
from typing import Dict, List
import datetime

@dataclass
class GuardState:
    last_suggestion_time: float = 0.0
    daily_count: int = 0
    last_reset_day: int = -1
    consecutive_rejections: int = 0

class SuggestionGuard:
    """
    Prevents spamming suggestions.
    Rules:
    - Max 1 suggestion per routine per day.
    - If rejected >= 2 times consecutively, suppress forever (or until manual reset).
    - Global cooldown (e.g. 1 hour) between ANY suggestions? (Optional, maybe simplistic for now)
    """
    
    def __init__(self):
        self._states: Dict[str, GuardState] = {} # Map routine_id -> GuardState
        
    def check_guard(self, routine_id: str, current_time: float) -> bool:
        """
        Returns True if safe to suggest.
        """
        # Ensure state exists
        if routine_id not in self._states:
            self._states[routine_id] = GuardState()
            
        state = self._states[routine_id]
        
        # Check suppression
        if state.consecutive_rejections >= 2:
            return False
            
        # Check daily limit
        # Simple day check using local day of month (flawed crossing months but fine for MVP)
        day = datetime.datetime.fromtimestamp(current_time).day
        if day != state.last_reset_day:
            state.daily_count = 0
            state.last_reset_day = day
            
        if state.daily_count >= 1:
            return False
            
        return True
        
    def record_suggestion(self, routine_id: str, current_time: float):
        if routine_id not in self._states:
             self._states[routine_id] = GuardState()
        state = self._states[routine_id]
        state.last_suggestion_time = current_time
        state.daily_count += 1
        
    def record_rejection(self, routine_id: str):
        if routine_id not in self._states:
            self._states[routine_id] = GuardState()
        self._states[routine_id].consecutive_rejections += 1

    def record_acceptance(self, routine_id: str):
         if routine_id in self._states:
            self._states[routine_id].consecutive_rejections = 0
