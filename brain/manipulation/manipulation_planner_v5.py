
import logging
from typing import Dict, List, Optional
from brain.manipulation.manipulation_planner_v4 import ManipulationPlannerV4
from brain.manipulation.manipulation_planner_v2 import Point3D, Trajectory3D
from brain.learning.policy_advisor import AdvisorySuggestion

logger = logging.getLogger(__name__)

class ManipulationPlannerV5(ManipulationPlannerV4):
    """
    Extensions:
    - Accepts advisory parameter deltas (e.g. lift_height).
    - Applies them to planning logic.
    """
    def __init__(self):
        super().__init__()
        self.default_params = {
            "lift_height": 0.05,
            "speed_scalar": 1.0
        }
    
    def plan_with_advisory(self, start: Point3D, end: Point3D, suggestions: List[AdvisorySuggestion]) -> Optional[Trajectory3D]:
        """
        Plans move using suggested params.
        """
        # 1. Apply Suggestions
        effective_params = self.default_params.copy()
        
        for sugg in suggestions:
            if sugg.parameter in effective_params:
                effective_params[sugg.parameter] += sugg.delta
                logger.info(f"Applying Advisory: {sugg.parameter} += {sugg.delta}")
        
        # 2. Plan (Using internal logic, here mocked extension of v4)
        # v4 checks 'outcome_memory'. v5 respects 'lift_height'.
        
        # Mock trajectory generation using effective params
        logger.info(f"Planning with Lift Height: {effective_params['lift_height']}")
        
        # Simple Linear + Lift
        # Lift up
        lift_pt = Point3D(start.x, start.y, start.z + effective_params['lift_height'])
        
        # ... (Simplified path for POC)
        traj = Trajectory3D(points=[start, lift_pt, end], duration=2.0)
        return traj

manipulation_planner_v5 = ManipulationPlannerV5()
