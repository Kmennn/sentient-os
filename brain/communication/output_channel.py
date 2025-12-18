from enum import StrEnum, auto

class OutputChannel(StrEnum):
    TOAST = auto()       # Visible Popup/Notification
    PANEL = auto()       # Passive Dashboard/Inbox
    LOG_ONLY = auto()    # Console/Audit only
    SUPPRESSED = auto()  # Blocked completely
