
import logging
from typing import List
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

logger = logging.getLogger(__name__)

class TrajectorySmoother:
    """
    Ensures trajectory continuity and smoothness.
    """
    def smooth(self, trajectory: Trajectory3D) -> Trajectory3D:
        """
        Applies a simple smoothing filter (e.g. moving average) to points.
        For POC, we just ensure no duplicate points and valid spacing.
        Future: Spline interpolation.
        """
        raw_points = trajectory.points
        if len(raw_points) < 3:
            return trajectory
            
        smoothed_points = [raw_points[0]] # Keep start fixed
        
        # Simple 3-point moving average for inner points
        for i in range(1, len(raw_points) - 1):
            prev = raw_points[i-1]
            curr = raw_points[i]
            next_p = raw_points[i+1]
            
            avg_x = (prev.x + curr.x + next_p.x) / 3.0
            avg_y = (prev.y + curr.y + next_p.y) / 3.0
            avg_z = (prev.z + curr.z + next_p.z) / 3.0
            
            smoothed_points.append(Point3D(avg_x, avg_y, avg_z))
            
        smoothed_points.append(raw_points[-1]) # Keep end fixed
        
        return Trajectory3D(smoothed_points, trajectory.duration)
        
trajectory_smoother = TrajectorySmoother()
