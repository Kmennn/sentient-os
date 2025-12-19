from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List
import time
import uuid
from brain.preferences.explicit_preference import ImportanceLevel

class ProposalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class AdjustmentProposal:
    domain: str
    current_importance: ImportanceLevel
    proposed_importance: ImportanceLevel
    reason: str
    confidence: float
    source_reflection_ids: List[str]
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    status: ProposalStatus = ProposalStatus.PENDING
    
    def to_dict(self):
        return {
            "proposal_id": self.proposal_id,
            "domain": self.domain,
            "current_importance": self.current_importance.value,
            "proposed_importance": self.proposed_importance.value,
            "reason": self.reason,
            "confidence": self.confidence,
            "source_reflection_ids": self.source_reflection_ids,
            "timestamp": self.timestamp,
            "status": self.status.value
        }
