from enum import Enum, auto
from brain.intents.intent import Intent, IntentPriority
from brain.intents.conflict_detector import ConflictReport
from brain.auth.role import UserRole

class Resolution(Enum):
    OVERRIDE = auto() # New replaces Active
    REJECT_NEW = auto() # New is rejected
    ESCALATE = auto() # Pause and wait for human decision

class ConflictPolicy:
    """
    Determines the resolution for a detected conflict.
    Rules:
    - Emergency Priority -> OVERRIDE
    - Higher Role -> OVERRIDE
    - Lower Role -> REJECT_NEW
    - Equal Role -> ESCALATE (unless Owner, who always wins against self? Actually no, Owner vs Owner is ambiguous -> Escalate/Queue, but for now ESCALATE)
    """

    def resolve(self, report: ConflictReport) -> Resolution:
        new = report.new_intent
        active = report.active_intent
        
        # 1. Emergency Bypass
        if new.priority == IntentPriority.EMERGENCY:
            return Resolution.OVERRIDE
            
        # 2. Strict Role Hierarchy
        # We need a proper comparison. Roles are enums, let's map to int values if needed or use defined comparison
        # Owner(1) < Operator(2)? No. default enum auto() values.
        # Let's verify Enum auto values order. In role.py: 
        # OWNER=auto() (1), OPERATOR=auto() (2), OBSERVER=auto() (3).
        # So actually Lower Value = Higher Authority generally in typical implementation, but let's check explicit logic.
        
        # Explicit logic is safer.
        new_rank = self._get_role_rank(new.role)
        active_rank = self._get_role_rank(active.role)
        
        if new_rank > active_rank: # Higher rank (numeric 3 > 2)
            return Resolution.OVERRIDE
        elif new_rank < active_rank:
            return Resolution.REJECT_NEW
        else:
            # Equal Rank
            # If both are Owners? -> Escalate.
            # If both are Operators? -> Escalate.
            return Resolution.ESCALATE

    def _get_role_rank(self, role: UserRole) -> int:
        """Higher integer = Higher Authority"""
        if role == UserRole.OWNER:
            return 3
        elif role == UserRole.OPERATOR:
            return 2
        elif role == UserRole.OBSERVER:
            return 1
        return 0
