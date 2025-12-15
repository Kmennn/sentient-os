
import logging
from typing import Optional
from brain.skills.skill_replay_engine import SkillReplayEngine
from brain.vision.object_semantics import object_registry, SemanticObject
from brain.skills.frame_alignment import frame_aligner
from brain.safety.affordance_guard import affordance_guard
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

logger = logging.getLogger(__name__)

class SkillReplayEngineV2(SkillReplayEngine):
    """
    Semantic-Aware & Orientation-Aware Replay.
    """
    def __init__(self):
        super().__init__()
        self.objects = object_registry
        self.aligner = frame_aligner
        self.affordance_guard = affordance_guard
        
    def replay_skill_on_object(self, skill_name: str, object_id: str, action_type: str = "use") -> bool:
        """
        Replay 'skill_name' relative to 'object_id'.
        """
        logger.info(f"Replay V2: '{skill_name}' on '{object_id}'")
        
        # 1. Get Object
        obj = self.objects.get_object(object_id)
        if not obj:
            logger.error(f"Object '{object_id}' not found.")
            return False
            
        # 2. Get Skill
        skill = self.memory.get_skill(skill_name)
        if not skill:
            logger.error(f"Skill '{skill_name}' not found.")
            return False

        # 3. Create Base Trajectory (Relative to Skill Origin)
        # Note: Skill points are relative to 0,0,0.
        # We treat Object Pose as the new Origin.
        base_points = [Point3D(p["x"], p["y"], p["z"]) for p in skill.points]
        duration = skill.metadata.get("duration", 2.0)
        base_traj = Trajectory3D(points=base_points, duration=duration)
        
        # 4. Align Trajectory to Object Frame (Rotation + Translation)
        # Construct target pose from Object
        target_pose = {
            "x": obj.position["x"],
            "y": obj.position["y"],
            "z": obj.position["z"],
            "orientation": obj.orientation
        }
        
        aligned_traj = self.aligner.align_trajectory(base_traj, target_pose)
        
        # 5. Semantic Safety Check
        if not self.affordance_guard.validate_interaction(obj, action_type, aligned_traj):
            logger.critical("Replay V2 blocked by Affordance Guard.")
            return False
            
        # 6. Physical Safety Check (v2.6)
        logger.info("Verifying Physical Safety...")
        if not self.guard.verify_plan(aligned_traj):
             logger.critical("Replay V2 blocked by Physical Guard.")
             return False
             
        # 7. Execute
        logger.info("Skill Verified. Executing...")
        self.replanner.execute_with_monitoring(aligned_traj)
        return True

skill_replay_v2 = SkillReplayEngineV2()
