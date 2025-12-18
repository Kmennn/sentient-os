from dataclasses import dataclass, field
import uuid
from brain.auth.role import UserRole

@dataclass
class User:
    name: str
    role: UserRole
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trust_override_permission: bool = False # Specific override for trusted operators

    @property
    def is_owner(self) -> bool:
        return self.role == UserRole.OWNER

    def can_override_trust(self) -> bool:
        """
        Check if user has special permission to override trust checks.
        Owners implicitly have this.
        """
        return self.is_owner or self.trust_override_permission
