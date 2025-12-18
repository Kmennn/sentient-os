from enum import StrEnum, auto

class InterruptStyle(StrEnum):
    ALWAYS_ASK = auto()          # Always ask permission for non-safety interrupts
    ASK_FOR_IMPORTANT = auto()   # Use logic/learning (Default)
    NEVER_INTERRUPT = auto()     # Never ask (Silence everything non-safety)
