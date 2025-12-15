
import logging
from typing import Optional
from brain.manipulation.manipulation_planner_v3 import ManipulationPlannerV3, Point3D, Trajectory3D
from brain.memory.physical_memory import physical_memory

logger = logging.getLogger(__name__)

class ManipulationPlannerV4(ManipulationPlannerV3):
    """
    Adaptive Planner (v4).
    Uses Physical Memory to adjust safety margins.
    """
    def __init__(self):
        super().__init__()
        self.memory = physical_memory
        
    def plan_reach(self, start: Point3D, target: Point3D) -> Optional[Trajectory3D]:
        # Determine Zone (Simplified: just use "default" or based on quadrant)
        zone_id = self._get_zone(target)
        
        # 1. Consult Memory
        suggested_clearance = self.memory.get_suggested_clearance(zone_id)
        
        # 2. Plan (Copy-paste logic from v2/v3 but with dynamic clearance)
        # Actually, v2 logic uses hardcoded 0.1m lift. 
        # I should override _interpolate or refactor v2 to accept clearance param.
        # But v2.plan_reach doesn't accept clearance.
        # I will re-implement plan_reach logic here using the suggested clearance.
        
        # Safety Check (v3 logic - already in super(), but we want to modify trajectory generation)
        # So we generate our own trajectory, then pass to super().check_path?
        # No, super().plan_reach calls check_path.
        
        # Let's override plan_reach completely, but reuse safety check from v3 if possible.
        # Actually v3 calls super().plan_reach.
        # I'll re-implement generation logic here.
        
        if target.z < self.safety_limit_z:
            target.z = self.safety_limit_z
            
        points = []
        
        # Dynamic Lift
        lift_height = max(start.z, target.z) + suggested_clearance 
        
        if suggested_clearance > 0.101: # Float tolerance
             logger.info(f"Planner V4: Adapting lift height to {lift_height:.2f}m (Clearance: {suggested_clearance:.2f}m)")
        
        # Waypoints
        p1 = Point3D(start.x, start.y, lift_height)
        points.append(p1)
        p2 = Point3D(target.x, target.y, lift_height)
        points.append(p2)
        points.append(target)
        
        # Interpolate
        full_path = self._interpolate(start, points)
        trajectory = Trajectory3D(full_path, duration=3.0)
        
        # 3. Safety Check (using V3's obstacle detector logic)
        # We can call the detector directly or use v3's infrastructure if we exposed it.
        # v3 has self.detector.
        
        is_safe, conflict = self.detector.check_path(trajectory)
        if not is_safe:
            logger.warning("Planner V4: Path blocked despite adaptation.")
            return None
            
        return trajectory

    def _get_zone(self, pt: Point3D) -> str:
        # Simple spatial hashing
        if pt.x > 0: return "right_side"
        return "left_side"

planner_v4 = ManipulationPlannerV4()
