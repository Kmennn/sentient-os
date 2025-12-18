from typing import Optional
from brain.devices.device_handoff import DeviceHandoff, HandoffReason

class HandoffDetector:
    """
    Detects when the active device changes and generates a handoff event.
    """
    def check_handoff(self, prev_device_id: Optional[str], new_device_id: Optional[str]) -> Optional[DeviceHandoff]:
        """
        Checks if a handoff occurred.
        """
        # If no previous device, it's just a startup or fresh activation, not a handoff
        if not prev_device_id:
            return None
            
        # If no new device (lost focus), not a handoff (just went idle)
        if not new_device_id:
            return None
            
        # If same device, no handoff
        if prev_device_id == new_device_id:
            return None
            
        # Context switch detected
        return DeviceHandoff(
            from_device_id=prev_device_id,
            to_device_id=new_device_id,
            reason=HandoffReason.FOCUS_SHIFT
        )
