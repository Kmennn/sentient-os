
import logging
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Point3D:
    x: float
    y: float
    z: float

@dataclass
class Trajectory3D:
    points: List[Point3D]
    duration: float

class ManipulationPlannerV2:
    def __init__(self):
        self.safety_limit_z = 0.05 # 5cm above table floor
        
    def plan_reach(self, start: Point3D, target: Point3D) -> Optional[Trajectory3D]:
        """
        Plan a simple reach: Up -> Over -> Down.
        """
        # Safety Check
        if target.z < self.safety_limit_z:
            logger.warning(f"Planner: Target too low ({target.z}m). Clamp to {self.safety_limit_z}")
            target.z = self.safety_limit_z
            
        points = []
        
        # 1. Lift from start (if needed)
        lift_height = max(start.z, target.z) + 0.1 # 10cm clearance
        current = Point3D(start.x, start.y, start.z)
        
        # Waypoint 1: Above Start
        p1 = Point3D(start.x, start.y, lift_height)
        points.append(p1)
        
        # Waypoint 2: Above Target
        p2 = Point3D(target.x, target.y, lift_height)
        points.append(p2)
        
        # Waypoint 3: At Target
        points.append(target)
        
        # Linear Interpolation between waypoints for smoothing (simplified)
        full_path = self._interpolate(start, points)
        
        return Trajectory3D(full_path, duration=3.0)

    def _interpolate(self, start: Point3D, waypoints: List[Point3D], steps=5) -> List[Point3D]:
        path = [start]
        current = start
        for wp in waypoints:
            for i in range(1, steps + 1):
                t = i / steps
                ix = current.x + (wp.x - current.x) * t
                iy = current.y + (wp.y - current.y) * t
                iz = current.z + (wp.z - current.z) * t
                path.append(Point3D(ix, iy, iz))
            current = wp
        return path

planner_v2 = ManipulationPlannerV2()
