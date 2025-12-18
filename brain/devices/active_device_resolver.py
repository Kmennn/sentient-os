from typing import Optional, Dict
import time
from brain.devices.active_device import ActiveDevice, InteractionType

class ActiveDeviceResolver:
    """
    Tracks device interactions and resolves the primary active device.
    Decays confidence over time.
    """
    def __init__(self):
        self._last_active: Optional[ActiveDevice] = None
        self._decay_window = 60.0 # seconds
        
    def report_interaction(self, device_id: str, interaction_type: InteractionType):
        """Update the active device signal."""
        # Input implies high immediate confidence
        # View implies lower
        self._last_active = ActiveDevice(
            device_id=device_id,
            last_interaction_ts=time.time(),
            interaction_type=interaction_type,
            confidence=1.0 # Reset to max on fresh interaction
        )
        
    def resolve(self) -> tuple[Optional[str], float]:
        """Returns (device_id, confidence). Confidence decays over time."""
        if not self._last_active:
            return None, 0.0
            
        age = self._last_active.age
        if age > self._decay_window:
            return None, 0.0
            
        # Linear decay: 1.0 at 0s -> 0.0 at 60s
        confidence = max(0.0, 1.0 - (age / self._decay_window))
        
        return self._last_active.device_id, confidence
