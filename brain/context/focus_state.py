from enum import StrEnum, auto

class FocusState(StrEnum):
    FREE = auto()
    MEETING = auto()        # Detected via Calendar
    FOCUS_SESSION = auto()  # Manually triggered
