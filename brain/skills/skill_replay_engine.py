
import logging
from typing import Optional
from brain.skills.skill_abstraction import SkillData
from brain.memory.skill_memory import skill_memory
from brain.robotics.robot_controller import robot_controller
from brain.manipulation.manipulation_planner_v3 import Trajectory3D, Point3D
from brain.manipulation.replanner import replanner
from brain.safety.physical_safety_guard import physical_safety_guard

logger = logging.getLogger(__name__)

class SkillReplayEngine:
    """
    Executes learned skills safely.
    """
    def __init__(self):
        self.memory = skill_memory
        self.robot = robot_controller
        self.guard = physical_safety_guard
        self.replanner = replanner

    def replay_skill(self, skill_name: str) -> bool:
        """
        Load skill, transform to current start, verify safety, execute.
        """
        logger.info(f"Replay Requested: {skill_name}")
        
        # 1. Load
        skill = self.memory.get_skill(skill_name)
        if not skill:
            logger.error(f"Skill '{skill_name}' not found.")
            return False
            
        # 2. Get Start Pose
        start_pose = self.robot.get_status()
        if not start_pose:
            return False
            
        start_x = start_pose.get("x", 0)
        start_y = start_pose.get("y", 0)
        start_z = start_pose.get("z", 0)
        
        # 3. Transform Trajectory
        points = []
        for pt in skill.points:
            # Add relative offset to current start
            px = start_x + pt["x"]
            py = start_y + pt["y"]
            pz = start_z + pt["z"]
            points.append(Point3D(px, py, pz))
            
        traj = Trajectory3D(points=points, duration=skill.metadata.get("duration", 2.0))
        
        # 4. Safety Guard Check
        if not self.guard.verify_plan(traj):
            logger.critical("Skill Replay BLOCKED by Safety Guard.")
            return False
            
        # 5. Execute via Replanner (Safety Monitoring)
        logger.info("Skill Verified. Executing...")
        # Replanner executes in thread, but here we might want to block or return?
        # Replanner.execute_with_monitoring is blocking-ish (simulated loop in thread)
        # But we need to know if it started.
        
        # We'll spawn it.
        self.replanner.execute_with_monitoring(traj)
        return True

skill_replay = SkillReplayEngine()
