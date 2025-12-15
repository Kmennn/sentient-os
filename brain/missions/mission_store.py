
import json
import os
import logging
from dataclasses import asdict
from typing import Optional, Dict, Any
from brain.missions.mission_contract import MissionContract, AutonomyLevel

logger = logging.getLogger(__name__)

class MissionStore:
    """
    Persists mission state to disk for recovery.
    Uses simple JSON file storage for this version.
    """
    def __init__(self, persistence_path: str = "brain/data/mission_store.json"):
        self.persistence_path = persistence_path
        self._ensure_dir()
        
    def _ensure_dir(self):
        dirname = os.path.dirname(self.persistence_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

    def save_checkpoint(self, contract: MissionContract, state: str, current_step_index: int):
        """
        Saves the current mission state.
        """
        data = {
            "mission_id": contract.mission_id,
            "contract": {
                "name": contract.name,
                "mission_id": contract.mission_id,
                "allowed_actions": contract.allowed_actions,
                "allowed_objects": contract.allowed_objects,
                "max_duration": contract.max_duration,
                "autonomy_level": contract.autonomy_level.name
            },
            "state": state,
            "current_step_index": current_step_index
        }
        
        try:
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Mission Checkpoint Saved: {contract.mission_id} [{state}]")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def load_active_mission(self) -> Optional[Dict[str, Any]]:
        """
        Loads the active mission if it exists.
        Returns a dictionary with contract data and state, or None.
        """
        if not os.path.exists(self.persistence_path):
            return None
            
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
                
            # Basic validation
            if "mission_id" not in data or "contract" not in data:
                return None
                
            return data
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def clear(self):
        if os.path.exists(self.persistence_path):
            os.remove(self.persistence_path)

mission_store = MissionStore()
