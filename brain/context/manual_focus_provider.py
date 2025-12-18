import time
from typing import Optional
from brain.context.focus_state import FocusState

class ManualFocusProvider:
    """
    Manages manually triggered focus sessions.
    """
    def __init__(self):
        self._focus_expiry: float = 0.0 # Epoch time
        
    def start_focus(self, duration_minutes: int):
        self._focus_expiry = time.time() + (duration_minutes * 60)
        
    def stop_focus(self):
        self._focus_expiry = 0.0
        
    def get_state(self) -> FocusState:
        if time.time() < self._focus_expiry:
            return FocusState.FOCUS_SESSION
        return FocusState.FREE
