from enum import Enum, auto
from brain.auth.delegation import Delegation
from typing import List

class ApprovalStatus(Enum):
    ALLOWED = auto()
    BLOCKED_CHAIN = auto()
    BLOCKED_LIMIT = auto()
    # Could add ESCALATED types later

class DelegationEscalationPolicy:
    """
    Decides whether to allow delegation usage based on Safety Checks.
    
    GOVERNANCE STABILITY DECLARATION (v6.3):
    This policy is FEATURE COMPLETE. No weakening of safety checks allowed.
    Bug fixes and optimizations only.
    """
    def __init__(self, limits, monitor):
        self.limits = limits
        self.monitor = monitor
        
    def evaluate_delegation_creation(self, delegator_id: str, delegations: List[Delegation]) -> ApprovalStatus:
        if not self.limits.check_limits(delegator_id, delegations):
            return ApprovalStatus.BLOCKED_LIMIT
        return ApprovalStatus.ALLOWED
        
    def evaluate_delegation_usage(self, delegation: Delegation, all_delegations: List[Delegation]) -> ApprovalStatus:
        if self.monitor.check_chain(delegation, all_delegations):
            return ApprovalStatus.BLOCKED_CHAIN
        return ApprovalStatus.ALLOWED
