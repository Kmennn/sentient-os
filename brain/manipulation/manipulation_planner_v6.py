
import logging
from typing import Dict, List, Optional
from brain.manipulation.manipulation_planner_v5 import ManipulationPlannerV5
from brain.manipulation.manipulation_planner_v2 import Point3D, Trajectory3D
from brain.learning.policy_advisor import AdvisorySuggestion
from brain.learning.blending_controller import BlendingController, blending_controller
from brain.learning.confidence_monitor import ConfidenceMonitor, confidence_monitor
from brain.explainability.blend_trace import BlendTrace, BlendTraceRecord, blend_trace

logger = logging.getLogger(__name__)

class ManipulationPlannerV6(ManipulationPlannerV5):
    """
    Hybrid Planner (v6).
    Blends Policy Intuition with Planning Rigor.
    """
    def __init__(self, 
                 blend_ctrl: BlendingController = blending_controller,
                 monitor: ConfidenceMonitor = confidence_monitor,
                 tracer: BlendTrace = blend_trace):
        super().__init__()
        self.blend_ctrl = blend_ctrl
        self.monitor = monitor
        self.tracer = tracer
        self.config_alpha = 1.0 # Default to Planner-Only (Pure safety)
        
    def set_alpha(self, alpha: float):
        """
        Set blending ratio. 1.0 = Pure Planner, 0.0 = Policy Authority.
        """
        self.config_alpha = max(0.0, min(1.0, alpha))
        logger.info(f"Planner V6: Alpha set to {self.config_alpha}")

    def plan_hybrid(self, start: Point3D, end: Point3D, suggestions: List[AdvisorySuggestion]) -> Optional[Trajectory3D]:
        """
        Plan with blending.
        """
        # 1. Check Confidence / Fail-Safe
        effective_alpha = self.config_alpha
        if not self.monitor.is_stable():
            logger.warning("Planner V6: Monitor reports instability. Reverting to Alpha=1.0")
            effective_alpha = 1.0
            
        # 2. Iterate Parameters & Blend
        effective_params = self.default_params.copy()
        
        for sugg in suggestions:
            param = sugg.parameter
            if param in effective_params:
                base_val = effective_params[param]
                # Sugg.delta is Policy contribution relative to base?
                # Actually, Advisor provided Delta.
                # Blend: final = Base + Delta * (1 - Alpha)
                
                final_val = self.blend_ctrl.compute_blend(param, base_val, sugg.delta, effective_alpha)
                
                effective_params[param] = final_val
                
                # Trace
                rec = BlendTraceRecord(param, base_val, sugg.delta, effective_alpha, final_val)
                self.tracer.generate_trace(rec)
                
        # 3. Execute Trajectory Gen (using blended params)
        # Mocking trajectory creation using effective params
        # (Same as V5 logic but params are now continuous blends)
        lift = effective_params['lift_height']
        
        # ... logic ...
        lift_pt = Point3D(start.x, start.y, start.z + lift)
        traj = Trajectory3D([start, lift_pt, end], duration=2.0)
        return traj

manipulation_planner_v6 = ManipulationPlannerV6()
