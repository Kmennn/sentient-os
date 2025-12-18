from enum import StrEnum, auto
import time
import uuid
from dataclasses import dataclass, field
from brain.intents.interrupt_reason import InterruptReason

class InterruptRequestStatus(StrEnum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()
    EXPIRED = auto()

@dataclass
class InterruptRequest:
    request_id: str
    reason: InterruptReason
    message: str
    created_at: float
    status: InterruptRequestStatus = InterruptRequestStatus.PENDING
    
    @staticmethod
    def create(reason: InterruptReason, message: str = ""):
        return InterruptRequest(
            request_id=str(uuid.uuid4()),
            reason=reason,
            message=message or f"May I interrupt you for {reason}?",
            created_at=time.time()
        )
