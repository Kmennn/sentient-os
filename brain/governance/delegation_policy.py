import time
from typing import List, Optional
from brain.auth.delegation import Delegation, DelegationScope

class DelegationPolicy:
    """
    Manages active delegations and verifies authority.
    
    GOVERNANCE STABILITY DECLARATION (v6.3):
    This policy is FEATURE COMPLETE. No new delegation powers or scopes allowed.
    Bug fixes and optimizations only.
    """
    def __init__(self):
        self.delegations: List[Delegation] = []

    def add_delegation(self, delegation: Delegation):
        self.delegations.append(delegation)

    def revoke_delegation(self, delegation_id: str):
        for d in self.delegations:
            if d.delegation_id == delegation_id:
                d.revoked = True

    def get_active_delegations(self, delegator_id: str = None) -> List[Delegation]:
        now = time.time()
        active = [d for d in self.delegations if not d.revoked and d.expires_at > now]
        if delegator_id:
            return [d for d in active if d.delegator_user_id == delegator_id]
        return active

    def check_authority(self, voter_id: str, required_approver_id: str, current_time: float = None) -> bool:
        """
        Returns True if voter_id IS the required_approver_id, 
        OR if voter_id has a valid delegation from required_approver_id.
        """
        if voter_id == required_approver_id:
            return True
            
        if current_time is None:
            current_time = time.time()
            
        # Check for delegation: required_approver (Delegator) -> voter (Delegate)
        valid_delegations = [
            d for d in self.delegations
            if d.delegator_user_id == required_approver_id
            and d.delegate_user_id == voter_id
            and not d.revoked
            and d.expires_at > current_time
        ]
        
        return len(valid_delegations) > 0
