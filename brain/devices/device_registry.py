from typing import Dict, List
import time
from brain.devices.device_identity import DeviceIdentity

class DeviceRegistry:
    """
    Tracks connected devices.
    In-memory storage for now.
    """
    def __init__(self):
        self._devices: Dict[str, DeviceIdentity] = {}
        
    def register_heartbeat(self, device_id: str, device_type: str, capabilities: List[str]):
        """Registers or updates a device's heartbeat."""
        now = time.time()
        if device_id in self._devices:
            self._devices[device_id].last_seen = now
            # Update capabilities/type if changed? usually static.
        else:
            try:
                # Import here to avoid circular dep if enum is used elsewhere, 
                # but DeviceType is in identity.py so it's fine.
                from brain.devices.device_identity import DeviceType
                dtype = DeviceType(device_type.lower())
            except ValueError:
                from brain.devices.device_identity import DeviceType
                dtype = DeviceType.DESKTOP # Default fallback
                
            self._devices[device_id] = DeviceIdentity(
                device_id=device_id,
                device_type=dtype,
                capabilities=capabilities,
                last_seen=now
            )
            
    def get_active_devices(self) -> List[DeviceIdentity]:
        self.prune()
        return [d for d in self._devices.values() if d.is_active]
        
    def prune(self):
        """Remove stale devices (inactive > 5 mins)."""
        now = time.time()
        timeout = 300 # 5 mins
        stale = [did for did, d in self._devices.items() if (now - d.last_seen) > timeout]
        for did in stale:
            del self._devices[did]
            
    def get_summary(self) -> str:
        active = self.get_active_devices()
        return f"{len(active)} active devices"

    def to_dict(self) -> Dict:
        return {
            "devices": {did: d.to_dict() for did, d in self._devices.items()}
        }
        
    @classmethod
    def from_dict(cls, data: Dict):
        registry = cls()
        if "devices" in data:
            for did, d_data in data["devices"].items():
                registry._devices[did] = DeviceIdentity.from_dict(d_data)
        return registry
