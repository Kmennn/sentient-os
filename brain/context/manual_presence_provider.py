from typing import Optional
from brain.context.presence_state import PresenceState

class ManualPresenceProvider:
    """
    Manages manual overrides for presence.
    """
    def __init__(self):
        self._override: Optional[PresenceState] = None
        
    def set_private(self):
        self._override = PresenceState.ALONE
        
    def set_public(self):
        self._override = PresenceState.WITH_OTHERS
        
    def clear(self):
        self._override = None
        
    def get_state(self) -> Optional[PresenceState]:
        return self._override
