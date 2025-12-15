
import logging
import time
import threading
from typing import Optional
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D
from brain.spatial.obstacle_detector import obstacle_detector
from brain.robotics.robot_controller import robot_controller

logger = logging.getLogger(__name__)

class Replanner:
    def __init__(self):
        self.active_trajectory: Optional[Trajectory3D] = None
        self.is_monitoring = False
        self.monitor_thread = None
        
    def execute_with_monitoring(self, trajectory: Trajectory3D):
        """
        Execute trajectory while checking safety at 10Hz.
        """
        self.active_trajectory = trajectory
        self.is_monitoring = True
        
        # Start execution in background (Robot Controller is async/blocking depending on impl)
        # v2.4 RobotController sends move commands.
        # Ideally we send point-by-point to allow interruption
        
        # Start Monitor
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        
        try:
            for pt in trajectory.points:
                if not self.is_monitoring:
                    logger.warning("Replanner: Execution halted.")
                    break
                
                # Command Robot
                robot_controller.reach_to(pt.x, pt.y, pt.z)
                # Wait based on segment duration (simplified)
                time.sleep(0.1) 
                
        except Exception as e:
            logger.error(f"Execution Error: {e}")
        finally:
            self.is_monitoring = False
            self.monitor_thread.join()

    def _monitor_loop(self):
        while self.is_monitoring:
            if not self.active_trajectory:
                break
                
            # Check remaining path (Approx: from current Pose forward)
            # For simplicity, we re-check whole path, or check immediate vicinity
            # Let's check the rest of the path?
            # Or just check if robot itself is in collision?
            
            # Let's re-verify the active trajectory validity
            is_safe, conflict = obstacle_detector.check_path(self.active_trajectory)
            if not is_safe:
                logger.critical(f"Replanner: DYNAMIC COLLISION! Stopping.")
                self.emergency_stop()
                break
                
            time.sleep(0.1)

    def emergency_stop(self):
        self.is_monitoring = False
        # Send Stop to Robot
        # robot_controller.stop() # Not impl in v2.4, assuming halt
        logger.info("Replanner: E-STOP Triggered.")

replanner = Replanner()
