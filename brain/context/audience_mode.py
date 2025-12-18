from enum import StrEnum, auto

class AudienceMode(StrEnum):
    PRIVATE = auto() # Alone
    PUBLIC = auto()  # With Others
    NEUTRAL = auto() # Unknown
