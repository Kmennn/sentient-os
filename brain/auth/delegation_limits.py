from brain.auth.delegation import Delegation
from typing import List

class DelegationLimits:
    """
    Enforces hard limits on delegation usage.
    """
    MAX_ACTIVE_KEY = "MAX_ACTIVE_DELEGATIONS"
    MAX_DURATION_SECONDS = 7 * 24 * 3600 # 7 days
    
    def check_limits(self, user_id: str, active_delegations: List[Delegation]) -> bool:
        """
        Check if user can create *more* delegations.
        """
        # Limit 1: Max active delegations (e.g. 3)
        if len(active_delegations) >= 3:
            return False
            
        return True

    def validate_duration(self, duration_seconds: int) -> bool:
        return duration_seconds <= self.MAX_DURATION_SECONDS
