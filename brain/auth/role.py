from enum import Enum, auto

class UserRole(Enum):
    OWNER = auto()     # Can approve anything, modify system settings
    OPERATOR = auto()  # Can execute normal missions, approve physical actions
    OBSERVER = auto()  # Read-only access, cannot approve or execute

    def can_approve_low_trust(self) -> bool:
        """Only OWNER can approve low trust missions"""
        return self == UserRole.OWNER

    def can_approve_physical(self) -> bool:
        """OPERATOR and OWNER can approve physical actions"""
        return self in (UserRole.OPERATOR, UserRole.OWNER)

    def can_execute_missions(self) -> bool:
        """OPERATOR and OWNER can execute missions"""
        return self in (UserRole.OPERATOR, UserRole.OWNER)
