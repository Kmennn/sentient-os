from typing import List, Optional
from brain.auth.user import User
from brain.auth.role import UserRole
from brain.missions.mission_contract import MissionContract

class ApprovalPolicy:
    """
    Central governance logic for determining if a user can approve a specific mission.
    """
    
    @staticmethod
    def can_approve(user: User, contract: MissionContract, is_low_trust_context: bool = False, has_physical_actions: bool = False) -> bool:
        """
        Determines if 'user' has authority to approve 'contract' given the context.
        """
        
        # 0. Observer Check - Observers cannot approve anything
        if user.role == UserRole.OBSERVER:
            return False
            
        # 1. Low Trust Context -> Owner Only
        if is_low_trust_context:
            if not user.is_owner:
                return False
                
        # 2. Physical Actions -> Operator or Owner
        if has_physical_actions:
            if not user.role.can_approve_physical():
                # This check is redundant since Observer is caught at step 0, 
                # but good for explicit logic if we add more roles later.
                return False

        # 3. Contract Specific Execution Role
        # If contract says "EXECUTION_ROLE = OWNER", then only OWNER can approve (effectively)
        # Because if Operator approved it, they are authorizing something above their paygrade?
        # Typically, the approver just needs to be >= the required execution role.
        if contract.execution_role:
             if contract.execution_role == UserRole.OWNER and not user.is_owner:
                 return False

        return True

    @staticmethod
    def get_denial_reason(user: User, contract: MissionContract, is_low_trust_context: bool = False, has_physical_actions: bool = False) -> Optional[str]:
        if user.role == UserRole.OBSERVER:
            return "Observers cannot approve missions."
            
        if is_low_trust_context and not user.is_owner:
            return "Low trust context requires OWNER approval."
            
        if has_physical_actions and not user.role.can_approve_physical():
            return "Physical actions require OPERATOR or OWNER approval."
            
        if contract.execution_role == UserRole.OWNER and not user.is_owner:
            return "Mission requires OWNER execution privileges."
            
        return None
