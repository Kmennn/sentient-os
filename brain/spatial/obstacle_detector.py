
import logging
import math
from typing import Tuple, List, Optional
from brain.spatial.spatial_mapper import spatial_mapper
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

logger = logging.getLogger(__name__)

class ObstacleDetector:
    def __init__(self):
        self.mapper = spatial_mapper
        self.safety_radius = 0.1 # 10cm radius around end-effector

    def check_path(self, trajectory: Trajectory3D) -> Tuple[bool, Optional[Point3D]]:
        """
        Check if trajectory collides with obstacles.
        Returns (is_safe, collision_point).
        """
        if not trajectory.points:
            return True, None
            
        for pt in trajectory.points:
            # Check a volume around the point
            # Simplified: check the single voxel at the point for now
            # In a real system, we'd check a sphere
            
            # Since Mapper is voxel grid, we sample points around pt
            if self.mapper.voxel_map.is_occupied(pt.x, pt.y, pt.z):
                logger.warning(f"Obstacle detected at ({pt.x:.2f}, {pt.y:.2f}, {pt.z:.2f})")
                return False, pt
                
            # Check Z floor safety
            if pt.z < 0.02: # Too close to table
                 logger.warning(f"Floor collision at ({pt.x:.2f}, {pt.y:.2f}, {pt.z:.2f})")
                 return False, pt

        return True, None

    def get_clearance(self, pt: Point3D) -> float:
        """
        Estimate distance to nearest obstacle.
        (Placeholder: returns 1.0 if free, 0.0 if occupied)
        """
        if self.mapper.voxel_map.is_occupied(pt.x, pt.y, pt.z):
            return 0.0
        return 1.0

obstacle_detector = ObstacleDetector()
