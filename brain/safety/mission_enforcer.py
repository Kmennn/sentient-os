
import logging
from brain.missions.mission_contract import MissionContract

logger = logging.getLogger(__name__)

class MissionViolationError(Exception):
    pass

class MissionEnforcer:
    """
    Enforces the boundaries defined in the MissionContract.
    Raises MissionViolationError if boundaries are breached.
    """
    def __init__(self, contract: MissionContract):
        self.contract = contract
        
    def validate_action(self, action_name: str, object_id: str):
        """
        Check if action and object are allowed.
        """
        # 1. Check Time
        if self.contract.is_expired():
            raise MissionViolationError("Mission Time Expired")
            
        # 2. Check Action
        if action_name not in self.contract.allowed_actions:
            raise MissionViolationError(f"Action '{action_name}' not allowed in mission scope.")
            
        # 3. Check Object
        if object_id not in self.contract.allowed_objects:
            raise MissionViolationError(f"Object '{object_id}' not allowed in mission scope.")
            
        # If passed
        return True

