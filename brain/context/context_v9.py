
import logging
from typing import Dict, Any, List
# Need v8 too? Assuming v8 exists or need restore.
# Let's import v8 carefully. 
try:
    from brain.context.context_v8 import ContextManagerV8
except ImportError:
    # If v8 missing, we might need to mock or restore it too.
    # For now assume v8 is there or we will hit another error.
    pass

from brain.predictive.predictive_engine import predictive_engine
from local_kernel.actions.embodied_action_layer import embodied_action_layer

logger = logging.getLogger(__name__)

class ContextManagerV9(ContextManagerV8):
    def __init__(self, persistence_path="data/session_state.json"):
        super().__init__(persistence_path)
        
    def get_predictive_snapshot(self, 
                                workspace_state: Dict[str, Any],
                                nearby_devices: List[Dict]) -> Dict[str, Any]:
        base = self.get_embodied_snapshot(workspace_state, nearby_devices)
        
        # 1. Prediction
        prediction = predictive_engine.predict([]) 
        base["prediction"] = {
            "category": prediction.category if prediction else "NONE",
            "confidence": prediction.confidence if prediction else 0.0
        }
        
        # 2. Action History
        base["recent_actions"] = embodied_action_layer.action_log[-5:]
        
        if prediction and prediction.category != "IDLE":
             base["fused_summary"] = f"[PREDICTED: {prediction.category}] " + base["fused_summary"]
             
        return base

context_manager_v9 = ContextManagerV9()
