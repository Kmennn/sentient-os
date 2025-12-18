from enum import StrEnum, auto
from dataclasses import dataclass
from brain.intents.interrupt_reason import InterruptReason

class PreferenceBias(StrEnum):
    LIKELY_ACCEPT = auto()
    LIKELY_REJECT = auto()
    NEUTRAL = auto()

@dataclass
class InterruptPreference:
    reason: InterruptReason
    approval_rate: float
    bias: PreferenceBias
    sample_size: int
