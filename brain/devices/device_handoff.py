from enum import StrEnum, auto
from dataclasses import dataclass
import time

class HandoffReason(StrEnum):
    FOCUS_SHIFT = auto() # Active user interaction on new device
    INACTIVITY = auto()  # Timeout on old device (implicit)
    USER_REQUEST = auto() # "Switch to phone" (explicit)

@dataclass
class DeviceHandoff:
    from_device_id: str
    to_device_id: str
    reason: HandoffReason
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
