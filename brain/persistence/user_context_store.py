import json
import os
import tempfile
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class UserContext:
    """
    Data Transfer Object for User Context.
    Monolith structure for persistence.
    """
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}

    @property
    def focus_patterns(self):
        return self.data.get("focus_patterns", [])

    @property
    def manual_focus_expiry(self):
        return self.data.get("manual_focus_expiry", 0.0)

    @property
    def interrupt_settings(self):
        return self.data.get("interrupt_settings", {})

    @property
    def interrupt_schedule(self):
        return self.data.get("interrupt_schedule", {})
        
    @property
    def presence_override(self):
        return self.data.get("presence_override", None)

class UserContextStore:
    """
    Persists User Context (Focus, Preferences) to JSON.
    """
    def __init__(self, file_path: str = "data/user_context.json"):
        self.file_path = file_path

    def save(self, 
             focus_patterns: list, 
             interrupt_settings: Any, 
             interrupt_schedule: Any, 
             manual_focus_expiry: float,
             presence_override: Optional[str]
             ):
        """
        Saves all context to disk.
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Serialize
            data = {
                "last_save": time.time(),
                "focus_patterns": [p.to_dict() for p in focus_patterns],
                "interrupt_settings": interrupt_settings.to_dict() if interrupt_settings else {},
                "interrupt_schedule": interrupt_schedule.to_dict() if interrupt_schedule else {},
                "manual_focus_expiry": manual_focus_expiry,
                "presence_override": presence_override 
            }
            
            # Atomic Write
            dir_name = os.path.dirname(self.file_path)
            with tempfile.NamedTemporaryFile(mode='w', dir=dir_name, delete=False, encoding='utf-8') as tf:
                json.dump(data, tf, indent=2)
                temp_name = tf.name
            
            os.replace(temp_name, self.file_path)
            
        except Exception as e:
            logger.error(f"Failed to save UserContext: {e}")
            if 'temp_name' in locals() and os.path.exists(temp_name):
                os.remove(temp_name)

    def load(self) -> UserContext:
        """Loads context. Returns empty UserContext if missing."""
        if not os.path.exists(self.file_path):
            return UserContext()
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return UserContext(data)
        except Exception as e:
            logger.error(f"Failed to load UserContext: {e}")
            return UserContext()
