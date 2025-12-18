from brain.context.presence_state import PresenceState

class AppPresenceProvider:
    """
    Detects presence context from active applications (e.g. Teams, Zoom).
    STUB implementation.
    """
    def get_state(self) -> PresenceState:
        # Check running processes? 
        # For MVP, return UNKNOWN or ALONE defaults.
        return PresenceState.UNKNOWN
