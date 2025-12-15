
import logging
import time
from typing import Optional
from brain.robotics.robot_controller import robot_controller
from brain.manipulation.manipulator_v2 import Point3D

logger = logging.getLogger(__name__)

class RetractionController:
    """
    Handles safe retraction in emergencies.
    """
    def __init__(self):
        self.robot = robot_controller
        self.safe_retract_dist = 0.1 # 10cm up

    def trigger_retraction(self) -> bool:
        """
        Immediately move the robot UP relative to current pose.
        """
        logger.warning("RetractionController: Triggering Safe Retraction!")
        
        # 1. Get current pose
        current = self.robot.get_status() # dict {x,y,z}
        if not current:
            logger.error("Retraction Failed: Could not get robot pose.")
            return False
            
        try:
            cur_z = current.get("z", 0.0)
            target_z = cur_z + self.safe_retract_dist
            
            # Clamp to ceiling (e.g. 0.8m) if we had one. 
            # For now, just go up.
            
            logger.info(f"Retracting from Z={cur_z:.3f} to Z={target_z:.3f}")
            
            # Execute immediate move
            # In real ROS, we might send a velocity command or high-priority pose
            success = self.robot.reach_to(
                current.get("x", 0),
                current.get("y", 0),
                target_z
            )
            return success
            
        except Exception as e:
            logger.error(f"Retraction Error: {e}")
            return False

retraction_controller = RetractionController()
