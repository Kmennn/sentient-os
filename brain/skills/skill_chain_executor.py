
import logging
from typing import List, Optional
from brain.tasks.task_graph_builder import TaskNode, task_graph_builder
from brain.skills.skill_replay_engine_v2 import skill_replay_v2
from brain.safety.inter_step_verifier import inter_step_verifier
from brain.explainability.physical_failure_explainer import physical_failure_explainer
from brain.spatial.occlusion_aware_planner import occlusion_planner
from brain.manipulation.replanner import replanner
from brain.manipulation.manipulator_v2 import Point3D
from brain.manipulation.manipulation_planner_v2 import Trajectory3D
from brain.vision.object_semantics import object_registry

logger = logging.getLogger(__name__)

class SkillChainExecutor:
    """
    Orchestrates multi-step tasks.
    """
    def __init__(self):
        self.replay = skill_replay_v2
        self.verifier = inter_step_verifier
        self.explainer = physical_failure_explainer
        self.planner = occlusion_planner
        self.replanner = replanner
        self.objects = object_registry

    def execute_chain(self, chain: List[TaskNode]) -> bool:
        logger.info(f"Starting Chain Execution ({len(chain)} steps)...")
        
        for i, node in enumerate(chain):
            logger.info(f"Step {i+1}/{len(chain)}: {node.skill_name} on {node.target_object_id}")
            
            # 1. Pre-Check Occlusion (for MOVE steps)
            if node.action_type == "move":
                if not self._check_path_safety(node):
                    logger.error(self.explainer.explain("OCCLUSION", {"x":0, "y":0})) # simplified context
                    return False

            # 2. Execute Skill
            success = self.replay.replay_skill_on_object(
                node.skill_name, 
                node.target_object_id,
                node.action_type
            )
            
            if not success:
                logger.error(f"Step '{node.id}' Execution Failed.")
                return False
                
            # 3. Verify Step
            if not self.verifier.verify_step_completion(node):
                 logger.error(self.explainer.explain("VERIFICATION_FAILED", {"details": node.id}))
                 return False
                 
        logger.info("Chain Execution Completed Successfully.")
        return True

    def _check_path_safety(self, node: TaskNode) -> bool:
        """
        Uses OcclusionPlanner to check if a path exists between current pose and target object.
        """
        # 1. Get Target Pos
        obj = self.objects.get_object(node.target_object_id)
        if not obj: return False
        
        target_pt = Point3D(obj.position["x"], obj.position["y"], obj.position["z"])
        
        # 2. Get Current Pos (Mock/Real)
        # Using (0,0,0) as placeholder for current effector pos if unavailable
        start_pt = Point3D(0,0,0) 
        
        # 3. Plan
        path = self.planner.plan_path(start_pt, target_pt)
        return path is not None

skill_chain_executor = SkillChainExecutor()
