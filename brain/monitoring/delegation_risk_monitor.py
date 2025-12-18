from typing import List
from brain.auth.delegation import Delegation

class DelegationRiskMonitor:
    """
    Detects risky patterns like delegation chains.
    
    GOVERNANCE STABILITY DECLARATION (v6.3):
    This monitor is FEATURE COMPLETE. No removal of risk checks allowed.
    Bug fixes and optimizations only.
    """
    
    def check_chain(self, delegation: Delegation, all_delegations: List[Delegation]) -> bool:
        """
        Returns True if a delegation chain is detected (User A -> User B -> User C).
        We want to prevent A -> B if B is running on behalf of C?
        Or rather, if User B delegates to C, check if someone delegated to B?
        
        Scenario: A -> B.
        If we find any delegation X -> A, then we have X -> A -> B. Chain.
        """
        # Check if the delegator (A) is a delegate in another active delegation
        for d in all_delegations:
             if d.delegate_user_id == delegation.delegator_user_id and not d.revoked:
                 return True # Chain detected
                 
        return False
