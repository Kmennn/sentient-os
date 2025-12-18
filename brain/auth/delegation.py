from dataclasses import dataclass, field
from enum import Enum, auto
import uuid
import time
from typing import Optional

class DelegationScope(Enum):
    ALL = auto() # Full authority
    MISSION_TYPE = auto() # Can approve specific mission types
    TIME_LIMITED_ONLY = auto() # Only valid for short term checks

@dataclass
class Delegation:
    """
    Represents a grant of authority from one user to another.
    """
    delegation_id: str
    delegator_user_id: str
    delegate_user_id: str
    scope: DelegationScope
    expires_at: float # Unix timestamp
    revoked: bool = False
    created_at: float = field(default_factory=time.time)

    @staticmethod
    def create(delegator: str, delegate: str, scope: DelegationScope, duration_seconds: int) -> 'Delegation':
        return Delegation(
            delegation_id=str(uuid.uuid4()),
            delegator_user_id=delegator,
            delegate_user_id=delegate,
            scope=scope,
            expires_at=time.time() + duration_seconds
        )
