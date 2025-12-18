from enum import StrEnum, auto

class ToneProfile(StrEnum):
    PERSONAL = auto() # Casual, direct ("You...")
    FORMAL = auto()   # Professional, passive ("System...")
    NEUTRAL = auto()  # Balanced
