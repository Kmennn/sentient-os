from dataclasses import dataclass, field
from typing import List, Dict, Optional
from brain.coplanning.coplan_proposal import CoPlanProposal

@dataclass
class SharedCoPlanProposal(CoPlanProposal):
    """
    Extends CoPlanProposal for multi-user contexts.
    """
    initiator_user_id: str = "unknown"
    required_approvers: List[str] = field(default_factory=list)
    approvals: Dict[str, bool] = field(default_factory=dict) # user_id -> approved?
    vetoed: bool = False
    override_reason: Optional[str] = None
