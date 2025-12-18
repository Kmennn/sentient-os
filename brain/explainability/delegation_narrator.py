from brain.auth.delegation import Delegation

import time

class DelegationNarrator:
    """
    Generates text regarding delegations.
    """
    
    def narrate_delegation(self, delegation: Delegation) -> str:
        if delegation.revoked:
            return f"Delegation from {delegation.delegator_user_id} revoked."
        
        status = "Active" if delegation.expires_at > time.time() else "Expired"
        return f"Delegated authority: {delegation.delegator_user_id} -> {delegation.delegate_user_id} ({status})."
