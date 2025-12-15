
import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

class SafetyEnvelope:
    """
    Validates Policy outputs against safety constraints.
    """
    def __init__(self):
        self.max_velocity = 1.0 # m/s
        self.min_clearance = 0.05 # 5cm
        
    def check_safety(self, trajectory: List[List[float]]) -> bool:
        """
        Trajectory: List of [x, y, z] points.
        """
        if not trajectory:
            return True

        points = np.array(trajectory)

        # 1. Check Workspace Bounds (Simulated floor check)
        min_z = np.min(points[:, 2])
        if min_z < 0.0:
            logger.warning(f"Safety Violation: Floor penetration Z={min_z:.2f}")
            return False
            
        if len(trajectory) < 2:
            return True
        
        # 2. Check Velocity
        diffs = np.diff(points, axis=0) # dx, dy, dz
        dists = np.linalg.norm(diffs, axis=1)
        # Assuming dt=0.1
        velocities = dists / 0.1
        
        max_v = np.max(velocities)
        if max_v > self.max_velocity:
            logger.warning(f"Safety Violation: Velocity {max_v:.2f} > {self.max_velocity}")
            return False
            

        return True

safety_envelope = SafetyEnvelope()
