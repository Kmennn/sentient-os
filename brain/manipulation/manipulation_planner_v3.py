
import logging
from typing import Optional
from brain.manipulation.manipulation_planner_v2 import ManipulationPlannerV2, Point3D, Trajectory3D
from brain.spatial.obstacle_detector import obstacle_detector

logger = logging.getLogger(__name__)

class ManipulationPlannerV3(ManipulationPlannerV2):
    """
    Obstacle-Aware Planner (v3).
    """
    def __init__(self):
        super().__init__()
        self.detector = obstacle_detector
    
    def plan_reach(self, start: Point3D, target: Point3D) -> Optional[Trajectory3D]:
        # 1. Generate Standard Path (v2 logic)
        trajectory = super().plan_reach(start, target)
        
        if not trajectory:
            return None
            
        # 2. Safety Check
        is_safe, conflict_pt = self.detector.check_path(trajectory)
        
        if not is_safe:
            logger.warning(f"Planner V3: Path blocked at ({conflict_pt.x:.2f}, {conflict_pt.y:.2f}). Aborting.")
            # In a real system, here we would trigger A* or RRT to find alternate path
            # For v2.5, "Safe Autonomy" means strict abort if unsafe
            return None
            
        logger.info("Planner V3: Path SAFE.")
        return trajectory

planner_v3 = ManipulationPlannerV3()
