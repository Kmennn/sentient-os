from enum import StrEnum, auto

class PresenceState(StrEnum):
    ALONE = auto()          # User is alone (Safe to talk)
    WITH_OTHERS = auto()    # User is public (Suppress sensitive info)
    UNKNOWN = auto()        # Default Conservative
