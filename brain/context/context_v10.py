
import logging
from typing import Dict, Any, List
from brain.context.context_v9 import ContextManagerV9

# Hardware Layers
from brain.perception.scene_interpreter_real import scene_interpreter_real
from local_kernel.audio.real_audio_stream import real_audio
from brain.embodiment.motion_model import motion_model
from brain.vision.depth_estimator import depth_estimator
from brain.robotics.robotics_interface import robot_interface

logger = logging.getLogger(__name__)

class ContextManagerV10(ContextManagerV9):
    """
    Hardware-aware context aggregation.
    """
    def __init__(self, persistence_path="data/session_state.json"):
        super().__init__(persistence_path)
        
    def get_hardware_snapshot(self, 
                              workspace_state: Dict[str, Any],
                              nearby_devices: List[Dict]) -> Dict[str, Any]:
        """
        Produce V10 snapshot.
        """
        base = self.get_predictive_snapshot(workspace_state, nearby_devices)
        
        # 1. Device Orientation
        base["motion"] = {
            "state": motion_model.state,
            "orientation": motion_model.get_orientation()
        }
        
        # 2. Audio Level (Instant)
        base["audio_level"] = real_audio.get_audio_level()
        
        # 3. Vision Status
        base["vision_feed"] = "MOCK" if scene_interpreter_real.is_mock else "LIVE"
        
        # 4. Robot State
        base["robot"] = {
            "gripper": robot_interface.gripper_state,
            "position": robot_interface.position
        }
        
        # Enrich summary
        if motion_model.state == "MOVING":
            base["fused_summary"] = "[DEVICE MOVING] " + base["fused_summary"]
            
        return base

context_manager_v10 = ContextManagerV10()
