from typing import Optional, Dict
from brain.context.context_window import ContextWindow

class ContextWindowManager:
    """
    Manages the ephemeral context window for cross-device handoff.
    Ensures only one active window exists and handles expiry.
    """
    def __init__(self):
        self._active_window: Optional[ContextWindow] = None
        
    def create_window(self, source_device_id: str, target_device_id: str, payload: Dict) -> ContextWindow:
        """Creates a new context window, overwriting any existing one."""
        window = ContextWindow(
            source_device_id=source_device_id,
            target_device_id=target_device_id,
            payload=payload
        )
        self._active_window = window
        return window
        
    def get_window(self, target_device_id: str) -> Optional[ContextWindow]:
        """Returns the active window if valid and matching target. Does not consume it."""
        if not self._active_window:
            return None
            
        if self._active_window.is_expired:
            self._active_window = None
            return None
            
        if self._active_window.target_device_id != target_device_id:
            # Wrong target device
            return None
            
        return self._active_window
        
    def consume_window(self, target_device_id: str) -> Optional[ContextWindow]:
        """Returns and clears the active window."""
        window = self.get_window(target_device_id)
        if window:
            self._active_window = None # Consumed
        return window
        
    def get_status(self):
        """Returns status for stream (safe)."""
        if not self._active_window or self._active_window.is_expired:
            return {"active": False, "source": None, "expires_in": 0.0}
            
        remaining = max(0.0, self._active_window.expires_at - time.time())
        return {
            "active": True,
            "source": self._active_window.source_device_id,
            "expires_in": remaining
        }
