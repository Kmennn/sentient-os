from typing import Dict, Optional
from brain.devices.device_registry import DeviceRegistry

class DeviceConfidenceManager:
    """
    Manages trust scores for devices by delegating to DeviceRegistry.
    Acts as a facade for confidence logic.
    """
    def __init__(self, registry: DeviceRegistry):
        self.registry = registry
        
    def register_interaction(self, device_id: str):
        if device_id in self.registry._devices:
            dev = self.registry._devices[device_id]
            dev.boost_trust()
        
    def get_score(self, device_id: str) -> float:
        """Returns the decayed, current score."""
        if device_id in self.registry._devices:
            return self.registry._devices[device_id].get_current_trust()
        return 0.5 # Default for unknown
        
    def get_level(self, device_id: str) -> str:
        score = self.get_score(device_id)
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.3:
            return "MED"
        else:
            return "LOW"
