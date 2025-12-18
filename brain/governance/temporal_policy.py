from brain.auth.role import UserRole
from brain.intents.intent import Intent

class TemporalPolicy:
    """
    Governs who can change the timing of missions (Defer, Reschedule, Expedite).
    """
    
    def can_defer(self, actor_role: UserRole, target_intent: Intent) -> bool:
        """
        Can the actor defer the target intent?
        """
        # Owners can defer anyone
        if actor_role == UserRole.OWNER:
            return True
            
        # Operators can defer themselves, but not Owners
        if actor_role == UserRole.OPERATOR:
            if target_intent.role == UserRole.OWNER:
                return False # Cannot defer superior
            if target_intent.role == UserRole.OPERATOR:
                # Can defer other operators or self? 
                # Let's say yes for now, peers can coordinate.
                return True
            # Operator can defer Observer implicitly
            return True 
            
        # Observers cannot defer anyone (read-only mostly)
        return False
