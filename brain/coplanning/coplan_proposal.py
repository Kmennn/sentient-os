from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Any
from brain.simulation.what_if_scenario import WhatIfScenario
import time

class ProposalStatus(Enum):
    PENDING = auto()
    APPLIED = auto()
    REVERTED = auto()
    CANCELLED = auto()

@dataclass
class CoPlanProposal:
    """
    Represents a proposed change waiting for consent or action.
    """
    proposal_id: str
    scenario: WhatIfScenario
    created_at: float = field(default_factory=time.time)
    status: ProposalStatus = ProposalStatus.PENDING
    undo_data: Optional[Dict[str, Any]] = None # To store state for reversion
