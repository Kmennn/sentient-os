from brain.communication.output_channel import OutputChannel
from brain.context.presence_state import PresenceState
from brain.communication.tone_profile import ToneProfile
from typing import List, Tuple
from brain.devices.device_identity import DeviceIdentity, DeviceType

class OutputRouter:
    """
    decides the delivery channel and target devices for a message.
    """
    def route(self, presence: PresenceState, tone: ToneProfile, suppressed: bool, is_safety: bool, active_devices: List[DeviceIdentity], active_device_id: str = None, device_confidence: float = 1.0) -> Tuple[OutputChannel, List[str]]:
        """
        Returns (Channel, List of Device IDs)
        """
        targets = []
        
        # 1. Suppression Check
        if suppressed:
            return OutputChannel.SUPPRESSED, []
            
        # 2. Safety Override (Broadcast) - Bypasses confidence
        if is_safety:
            # Send to all capable devices
            targets = [d.device_id for d in active_devices if "TOAST" in d.capabilities or "AUDIO" in d.capabilities]
            # Fallback if no caps
            if not targets and active_devices:
                targets = [d.device_id for d in active_devices]
            return OutputChannel.TOAST, targets
            
        # 3. Confidence Check (Security/Trust)
        # Identify the confidence of the active device.
        # If very low, we suppress everything except safety.
        if device_confidence < 0.15:
            # Very Low Confidence (Untrusted/Stale) -> Suppress Output
            return OutputChannel.SUPPRESSED, []
            
        # Select Channel
        channel = OutputChannel.PANEL # Default
        if presence == PresenceState.WITH_OTHERS:
            channel = OutputChannel.PANEL
        elif presence == PresenceState.ALONE:
            channel = OutputChannel.TOAST
            
        # 4. Confidence-Based Downgrade
        # If confidence is Low (< 0.3) but not critically low, we downgrade TOAST to PANEL.
        # This prevents intrusive notifications on barely-trusted devices.
        if channel == OutputChannel.TOAST and device_confidence < 0.3:
            channel = OutputChannel.PANEL
            
        # Select Targets based on Channel & Active Device
        if channel == OutputChannel.PANEL:
            # Panel mostly for Desktop / Tablet
            targets = [d.device_id for d in active_devices if d.device_type in [DeviceType.DESKTOP, DeviceType.TABLET]]
        
        elif channel == OutputChannel.TOAST:
            # Toast Logic:
            # 1. If we have a HIGH INTERACTION active device, targeting it is best.
            # 2. Otherwise fall back to all personal devices.
            
            # Check if active_device_id is valid and in active_devices
            active_dev_obj = next((d for d in active_devices if d.device_id == active_device_id), None)
            
            if active_device_id and active_dev_obj:
                 # Prioritize CURRENTLY FOCUSED device
                 targets = [active_device_id]
            else:
                # Fallback: All Personal Devices
                targets = [d.device_id for d in active_devices if d.device_type in [DeviceType.DESKTOP, DeviceType.MOBILE]]
            
        if not targets and active_devices:
             # Fallback to at least one device output if we have active devices
             targets = [active_devices[0].device_id]
             
        return channel, targets
