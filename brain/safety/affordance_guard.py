
import logging
from brain.affordances.affordance_engine import affordance_engine
from brain.vision.object_semantics import SemanticObject
from brain.manipulation.manipulation_planner_v2 import Trajectory3D

logger = logging.getLogger(__name__)

class AffordanceGuard:
    """
    Enforces semantic safety constraints.
    """
    def __init__(self):
        self.engine = affordance_engine
        
    def validate_interaction(self, obj: SemanticObject, action: str, trajectory: Trajectory3D) -> bool:
        """
        Check if action is allowed on object AND if trajectory parameters are safe for that object.
        """
        # 1. Semantic Check
        if not self.engine.is_action_allowed(obj, action):
            logger.critical(f"Affordance Guard: Action '{action}' forbidden on '{obj.label}'.")
            return False
            
        # 2. Physical Check (Speed/Force based on properties)
        # speed = dist / duration
        start = trajectory.points[0]
        end = trajectory.points[-1]
        dist = ((start.x-end.x)**2 + (start.y-end.y)**2 + (start.z-end.z)**2)**0.5
        duration = max(trajectory.duration, 0.1)
        speed = dist / duration
        
        # Rule: Fragile objects -> max speed 0.2 m/s
        if obj.properties.is_fragile and speed > 0.2:
            logger.critical(f"Affordance Guard: Action too fast ({speed:.2f} m/s) for fragile object '{obj.label}'.")
            return False
            
        # Rule: Heavy objects -> max speed 0.1 m/s (safety)
        if obj.properties.is_heavy and speed > 0.1:
            logger.critical(f"Affordance Guard: Action too fast ({speed:.2f} m/s) for heavy object '{obj.label}'.")
            return False
            
        return True

affordance_guard = AffordanceGuard()
