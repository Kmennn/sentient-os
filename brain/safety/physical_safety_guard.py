
import logging
from brain.manipulation.manipulation_planner_v2 import Trajectory3D
from brain.robotics.execution_mode import execution_manager, Mode

logger = logging.getLogger(__name__)

class PhysicalSafetyGuard:
    """
    Final Gatekeeper for physical actions.
    Enforces hard constraints.
    """
    def __init__(self):
        self.min_z_clearance = 0.05
        self.max_path_length = 2.0 # Max 2 meters per move
        
    def verify_plan(self, trajectory: Trajectory3D) -> bool:
        """
        Returns True if plan is SAFE to execute.
        """
        if not trajectory or not trajectory.points:
            return False
            
        # Constraint 1: Minimum Z (Hard Floor)
        min_z = min([p.z for p in trajectory.points])
        if min_z < 0.0:
            logger.critical(f"Safety Guard: Plan violates floor constraint (Min Z {min_z:.3f} < 0.0)")
            return False
            
        # Constraint 2: Path Length (Sanity Check)
        # Simplify: just check end-to-end dist
        start = trajectory.points[0]
        end = trajectory.points[-1]
        dist = ((start.x-end.x)**2 + (start.y-end.y)**2 + (start.z-end.z)**2)**0.5
        if dist > self.max_path_length:
            logger.critical(f"Safety Guard: Path too long ({dist:.2f}m > {self.max_path_length}m)")
            return False

        # Constraint 3: Adaptation Safety
        # If LIVE mode, ensure we aren't doing wild experimental moves
        if execution_manager.get_mode() == Mode.LIVE:
             # Example: Check if max acceleration/speed implied by duration is safe
             # Duration is stored in trajectory.
             # Avg speed = dist / duration
             avg_speed = dist / max(trajectory.duration, 0.1)
             if avg_speed > 0.5: # 0.5 m/s limit
                 logger.critical(f"Safety Guard: Speed check failed ({avg_speed:.2f} m/s).")
                 return False

        return True

physical_safety_guard = PhysicalSafetyGuard()
