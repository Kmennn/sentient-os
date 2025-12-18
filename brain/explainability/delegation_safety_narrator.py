from brain.governance.delegation_escalation_policy import ApprovalStatus

class DelegationSafetyNarrator:
    """
    Explains why a delegation action was blocked or warned.
    """
    
    def narrate_block(self, status: ApprovalStatus) -> str:
        if status == ApprovalStatus.BLOCKED_CHAIN:
            return "Delegation blocked: Chain detected (Cannot delegate delegated authority)."
        if status == ApprovalStatus.BLOCKED_LIMIT:
            return "Delegation blocked: Maximum active delegations reached."
        return "Delegation blocked by policy."
