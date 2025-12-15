
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class VisionState:
    camera_active: bool = False
    objects_detected: int = 0
    last_frame_ts: float = 0.0

@dataclass
class AudioState:
    mic_active: bool = False
    noise_level: float = 0.0
    is_speaking: bool = False

@dataclass
class SystemBodyState:
    cpu_load: float = 0.0
    battery_level: float = 100.0
    thermal_status: str = "NORMAL"

@dataclass
class DeviceOrientation:
    orientation: str = "LANDSCAPE"
    tilt_angle: float = 0.0

@dataclass
class BodyPacket:
    timestamp: float
    vision: VisionState
    audio: AudioState
    system: SystemBodyState
    device: DeviceOrientation

class EmbodiedIntelligenceLayer:
    def __init__(self):
        self.vision = VisionState()
        self.audio = AudioState()
        self.system = SystemBodyState()
        self.device = DeviceOrientation()
        
    def update_vision(self, active: bool, objects: int):
        self.vision.camera_active = active
        self.vision.objects_detected = objects
        self.vision.last_frame_ts = time.time()
        
    def update_audio(self, active: bool, noise: float, speaking: bool):
        self.audio.mic_active = active
        self.audio.noise_level = noise
        self.audio.is_speaking = speaking
        
    def update_system(self, cpu: float, battery: float):
        self.system.cpu_load = cpu
        self.system.battery_level = battery
        
    def get_body_state(self) -> BodyPacket:
        return BodyPacket(
            timestamp=time.time(),
            vision=self.vision,
            audio=self.audio,
            system=self.system,
            device=self.device
        )

eil = EmbodiedIntelligenceLayer()
