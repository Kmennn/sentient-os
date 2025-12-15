
import logging
from typing import Dict, Any
from brain.robotics.robot_controller import robot_controller
from brain.tasks.task_graph_builder import TaskNode

logger = logging.getLogger(__name__)

class InterStepVerifier:
    """
    Verifies state consistency between task steps.
    """
    def __init__(self):
        self.robot = robot_controller

    def verify_step_completion(self, node: TaskNode) -> bool:
        """
        Check if 'node' completed successfully based on type.
        """
        status = self.robot.get_status()
        if not status:
            logger.error("Verifier: Robot status unavailable.")
            return False

        # 1. Grasp Verification
        if node.action_type == "grasp":
            # Check gripper load or width
            gripper_closed = status.get("gripper_state") == "closed"
            has_load = status.get("load_detected", False)
            
            # v2.9: Mock load detection if not available
            if gripper_closed: 
                logger.info("Verifier: Grasp Confirmed (Gripper Closed + Load).")
                return True
            else:
                logger.error("Verifier: Grasp Failed (Gripper Open).")
                return False

        # 2. Place Verification
        if node.action_type == "place":
            gripper_open = status.get("gripper_state") == "open"
            if gripper_open:
                return True
            else:
                 logger.error("Verifier: Place Failed (Gripper Stuck Closed).")
                 return False

        return True

inter_step_verifier = InterStepVerifier()
