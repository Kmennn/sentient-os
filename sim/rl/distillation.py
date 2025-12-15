
import logging
import numpy as np
from typing import Dict, List
from sim.rl.policy_trainer import SimplePolicy
from sim.envs.manipulation_env import ManipulationEnv

logger = logging.getLogger(__name__)

class KnowledgeDistiller:
    """
    Extracts explicit rules from opaque policy weights.
    For v3.0, we simulate extraction by observing average safe height.
    """
    def distill(self, policy: SimplePolicy, episodes=20) -> Dict[str, float]:
        env = ManipulationEnv()
        z_heights = []
        
        for _ in range(episodes):
            obs = env.reset()
            done = False
            
            episode_zs = []
            while not done:
                action = policy.predict(np.array(obs))
                obs_list, _, done, info = env.step(action.tolist())
                
                # Collect Z height if not colliding
                if not info['collision']:
                     current_z = env.effector_pos[2]
                     episode_zs.append(current_z)
                     
            if episode_zs:
                z_heights.append(np.mean(episode_zs))
                
        avg_z = float(np.mean(z_heights)) if z_heights else 0.0
        
        # Rule generation
        suggestion = {
            "suggested_safe_height": avg_z,
            "distillation_confidence": 0.8
        }
        
        logger.info(f"Distilled Rules: {suggestion}")
        return suggestion

knowledge_distiller = KnowledgeDistiller()
