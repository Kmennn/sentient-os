
import logging
from typing import Dict, Any, List
# V8 depends on V7... assuming V7 exists.
try:
    from brain.context.context_v7 import ContextManagerV7
except ImportError:
    # Minimal mock if V7 missing
    class ContextManagerV7:
        def __init__(self, p): pass
        def get_governed_snapshot(self, ws, nd): 
            return {"fused_summary": "Base"}

from brain.embodiment.eil import eil
from brain.sensors.sensor_fusion import sfe
from brain.attention.bi_modal_attention import attention_model

logger = logging.getLogger(__name__)

class ContextManagerV8(ContextManagerV7):
    def __init__(self, persistence_path="data/session_state.json"):
        super().__init__(persistence_path)
        
    def get_embodied_snapshot(self, 
                              workspace_state: Dict[str, Any],
                              nearby_devices: List[Dict]) -> Dict[str, Any]:
        base = self.get_governed_snapshot(workspace_state, nearby_devices)
        body = eil.get_body_state()
        base["body"] = {
            "vision_active": body.vision.camera_active,
            "audio_active": body.audio.mic_active,
            "noise_level": body.audio.noise_level
        }
        mode = workspace_state.get("mode", "IDLE")
        situation = sfe.fuse(body, mode)
        base["situation"] = situation
        base["attention_focus"] = attention_model.get_focus()
        
        if situation["attention_demand"] > 0.8:
            base["fused_summary"] = f"[HIGH ATTENTION: {situation['high_level_desc']}] " + base["fused_summary"]
            
        return base

context_manager_v8 = ContextManagerV8()
