import json
import os
import tempfile
import logging
from typing import Optional
from brain.devices.device_registry import DeviceRegistry

logger = logging.getLogger(__name__)

class DeviceRegistryStore:
    """
    Persists DeviceRegistry to JSON file.
    Atomic writes.
    """
    def __init__(self, file_path: str = "data/device_registry.json"):
        self.file_path = file_path
        
    def save(self, registry: DeviceRegistry):
        """Saves registry to disk atomically."""
        try:
            # Ensure dir exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            data = registry.to_dict()
            
            # Write to temp file first
            dir_name = os.path.dirname(self.file_path)
            with tempfile.NamedTemporaryFile(mode='w', dir=dir_name, delete=False, encoding='utf-8') as tf:
                json.dump(data, tf, indent=2)
                temp_name = tf.name
            
            # Atomic move
            os.replace(temp_name, self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to save DeviceRegistry: {e}")
            if 'temp_name' in locals() and os.path.exists(temp_name):
                os.remove(temp_name)

    def load(self) -> Optional[DeviceRegistry]:
        """Loads registry from disk. Returns None if invalid/missing."""
        if not os.path.exists(self.file_path):
            return None
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return DeviceRegistry.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load DeviceRegistry: {e}")
            return None
