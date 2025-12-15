
import logging
import time
from typing import Dict, Tuple
from brain.robotics.ros_bridge import ros_bridge

logger = logging.getLogger(__name__)

class RobotController:
    """
    High-level controller for robotic actions.
    Abstraction layer above ROS bridge.
    """
    def __init__(self):
        self.bridge = ros_bridge

    def reach_to(self, x: float, y: float, z: float) -> bool:
        """
        Command robot to coordinate.
        """
        logger.info(f"RobotController: Reaching to ({x}, {y}, {z})")
        return self.bridge.publish_move({"x": x, "y": y, "z": z})

    def grasp_object(self) -> bool:
        logger.info("RobotController: Grasping")
        return self.bridge.publish_grasp(release=False)

    def release_object(self) -> bool:
        logger.info("RobotController: Releasing")
        return self.bridge.publish_grasp(release=True)

    def get_status(self) -> Dict[str, float]:
        return self.bridge.get_pose()

    def is_ready(self) -> bool:
        return self.bridge.connected

robot_controller = RobotController()
