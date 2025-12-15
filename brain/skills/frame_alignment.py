
import logging
import math
from typing import Dict, List, Tuple
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

logger = logging.getLogger(__name__)

class FrameAligner:
    """
    Handles coordinate frame transformations for skills.
    Simplified 2D rotation (Z-axis) for v2.8.
    """
    def align_trajectory(self, trajectory: Trajectory3D, target_pose: Dict[str, float]) -> Trajectory3D:
        """
        Rotates and translates trajectory to match target pose (x, y, z, yaw).
        Assumes trajectory origin is (0,0,0) and facing +X.
        """
        # Target
        tx = target_pose.get("x", 0)
        ty = target_pose.get("y", 0)
        tz = target_pose.get("z", 0)
        yaw = target_pose.get("orientation", {}).get("yaw", 0) # In radians
        
        cos_theta = math.cos(yaw)
        sin_theta = math.sin(yaw)
        
        new_points = []
        for pt in trajectory.points:
            # 1. Rotate (around Z)
            rx = pt.x * cos_theta - pt.y * sin_theta
            ry = pt.x * sin_theta + pt.y * cos_theta
            rz = pt.z # No pitch/roll adjustment yet
            
            # 2. Translate
            fx = rx + tx
            fy = ry + ty
            fz = rz + tz
            
            new_points.append(Point3D(fx, fy, fz))
            
        return Trajectory3D(points=new_points, duration=trajectory.duration)

frame_aligner = FrameAligner()
