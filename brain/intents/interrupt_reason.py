from enum import StrEnum, auto

class InterruptReason(StrEnum):
    SAFETY = auto()             # Immediate physical, security, or data loss risk
    DEADLINE_RISK = auto()      # Failure to act leads to missed deadline
    USER_DEPENDENCY = auto()    # System is blocked waiting for user input
    OPTIMIZATION = auto()       # Non-urgent improvement suggestion
