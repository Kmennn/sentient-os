
import logging
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)

class ResourceLockManager:
    """
    Manages exclusive access to hardware resources (arms, cameras, etc.).
    Prevents race conditions between missions.
    """
    def __init__(self):
        # resource_id -> owning_mission_id
        self._locks: Dict[str, str] = {}
        
    def acquire(self, mission_id: str, resource_id: str) -> bool:
        """
        Try to acquire a lock.
        Returns True if successful (acquired or already owned), False if held by another.
        """
        owner = self._locks.get(resource_id)
        if owner is None:
            self._locks[resource_id] = mission_id
            logger.info(f"Lock ACQUIRED: {resource_id} by {mission_id}")
            return True
        elif owner == mission_id:
            return True # Re-entrant OK
        else:
            logger.warning(f"Lock DENIED: {resource_id} held by {owner}, requested by {mission_id}")
            return False
            
    def release(self, mission_id: str, resource_id: str):
        """
        Release a lock if held by mission_id.
        """
        owner = self._locks.get(resource_id)
        if owner == mission_id:
            del self._locks[resource_id]
            logger.info(f"Lock RELEASED: {resource_id} by {mission_id}")
            
    def release_all(self, mission_id: str):
        """
        Release ALL locks held by this mission (cleanup).
        """
        to_release = [res for res, owner in self._locks.items() if owner == mission_id]
        for res in to_release:
            del self._locks[res]
        if to_release:
            logger.info(f"Released {len(to_release)} locks for {mission_id}")

    def is_locked(self, resource_id: str) -> bool:
        return resource_id in self._locks

resource_lock_manager = ResourceLockManager()
