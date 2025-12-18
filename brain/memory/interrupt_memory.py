from typing import Dict, List
from brain.intents.interrupt_reason import InterruptReason

class InterruptMemory:
    """
    Stores historical outcomes of interrupt requests specific to reasons.
    """
    def __init__(self):
        # reason -> list of outcomes (True=Approved, False=Rejected)
        self._history: Dict[InterruptReason, List[bool]] = {}
        self._window_size = 10 # Rolling window
        
    def record_outcome(self, reason: InterruptReason, approved: bool):
        if reason not in self._history:
            self._history[reason] = []
        
        self._history[reason].append(approved)
        # Keep window
        if len(self._history[reason]) > self._window_size:
            self._history[reason].pop(0)
            
    def get_history(self, reason: InterruptReason) -> List[bool]:
        return self._history.get(reason, [])
        
    def get_all_history(self) -> Dict[InterruptReason, List[bool]]:
        return self._history
