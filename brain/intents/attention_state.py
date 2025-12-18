from enum import StrEnum, auto

class AttentionState(StrEnum):
    EXPLICIT = auto()  # User directly initiated (e.g. clicked button)
    INTERRUPT = auto() # System initiated, interrupts user
    PASSIVE = auto()   # Background or system tick, no interruption
