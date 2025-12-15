
import logging
import time
from typing import Dict, Any, List

from brain.spatial.spatial_mapper import spatial_mapper
from brain.robotics.robot_controller import robot_controller
from brain.manipulation.manipulation_planner_v2 import planner_v2, Point3D

logger = logging.getLogger(__name__)

class SpatialAutonomyEngine:
    """
    Decides actions based on spatial changes.
    """
    def __init__(self):
        self.active = False
        self.last_check_ts = 0
        
    def start_loop(self):
        self.active = True
        logger.info("Spatial Autonomy: Started.")

    def stop_loop(self):
        self.active = False
        logger.info("Spatial Autonomy: Stopped.")

    def tik_tok(self):
        """
        Called periodically (e.g. 1Hz) to check environment.
        """
        if not self.active: return
        
        # 1. Check Spatial Map for "clutter"
        occupied_count = spatial_mapper.get_occupied_voxels()
        if occupied_count > 1000:
            logger.info(f"Autonomy: High clutter detected ({occupied_count} voxels).")
            # Logic: Maybe notify user or clean up?
            # For now, just log.

        # 2. Check for robot readiness
        if robot_controller.is_ready():
             # Example: If something is at (0.5, 0.5, 0.1), pick it up?
             if spatial_mapper.voxel_map.is_occupied(0.5, 0.5, 0.1):
                 logger.info("Autonomy: Object found at (0.5,0.5). Planning grasp.")
                 self.execute_grasp(0.5, 0.5, 0.1)

    def execute_grasp(self, x, y, z):
        # 1. Plan
        start = Point3D(*robot_controller.get_status().values()) if robot_controller.is_ready() else Point3D(0,0,0)
        target = Point3D(x, y, z)
        
        traj = planner_v2.plan_reach(start, target)
        
        if traj:
            logger.info("Autonomy: Planning successful. Executing.")
            robot_controller.reach_to(x, y, z)
            time.sleep(1) # Wait for move
            robot_controller.grasp_object()
        else:
            logger.warning("Autonomy: Planning failed (Safety/Reachability).")

spatial_autonomy = SpatialAutonomyEngine()
