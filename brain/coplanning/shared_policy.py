from enum import Enum, auto

class UserRole(Enum):
    OWNER = auto()
    ADMIN = auto()
    OPERATOR = auto()
    OBSERVER = auto()

class SharedPolicy:
    """
    Defines permissions for Co-Planning based on User Role and Trust.
    
    GOVERNANCE STABILITY DECLARATION (v6.3):
    This policy is FEATURE COMPLETE. No new roles or override paths allowed.
    Bug fixes and optimizations only.
    """
    
    def can_approve(self, role: UserRole, trust_score: float) -> bool:
        # Observers can never approve
        if role == UserRole.OBSERVER:
            return False
            
        # Operators need high trust (> 0.5)
        if role == UserRole.OPERATOR and trust_score < 0.5:
             return False
             
        return True
        
    def can_override(self, role: UserRole) -> bool:
        # Only Owner and Admin can override
        return role in [UserRole.OWNER, UserRole.ADMIN]
        
    def can_veto(self, role: UserRole) -> bool:
        # Anyone with approval rights can veto? 
        # For safety, let's say yes, even Operators.
        return role != UserRole.OBSERVER
