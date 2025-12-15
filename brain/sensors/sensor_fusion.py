
import logging
from typing import Dict, Any, List
from brain.embodiment.eil import BodyPacket

logger = logging.getLogger(__name__)

class SensorFusionEngine:
    def __init__(self):
        pass
        
    def fuse(self, body_state: BodyPacket, workspace_mode: str) -> Dict[str, Any]:
        situation = {
            "high_level_desc": "Unknown",
            "attention_demand": 0.0,
            "social_context": "Alone"
        }
        if body_state.vision.objects_detected > 0:
            situation["social_context"] = "Presence Detected"
        if body_state.audio.is_speaking:
            situation["high_level_desc"] = "User Speaking"
            situation["attention_demand"] = 0.9
        elif workspace_mode == "WORK":
            situation["high_level_desc"] = "Deep Work"
            situation["attention_demand"] = 0.2
        elif body_state.audio.noise_level > 0.7:
            situation["high_level_desc"] = "Noisy Environment"
        return situation

sfe = SensorFusionEngine()
