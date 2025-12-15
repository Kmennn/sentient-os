
import numpy as np
import logging
from typing import Dict, List
from sim.envs.manipulation_env import ManipulationEnv
from sim.envs.scenario_generator import ScenarioGenerator
from sim.rl.policy_trainer import SimplePolicy

logger = logging.getLogger(__name__)

class StabilityEvaluator:
    """
    Measures policy robustness across randomized scenarios.
    """
    def evaluate(self, policy: SimplePolicy, difficulty: int = 1, runs: int = 20) -> Dict[str, float]:
        env = ManipulationEnv()
        gen = ScenarioGenerator()
        rewards = []
        failures = 0
        
        for i in range(runs):
            # Generate Scenario
            target, obstacles, start = gen.generate(difficulty, seed=1000+i)
            
            # Configure Env (We need to update Env to accept config)
            # For now, we mock this injection since Env doesn't support explicit config injection yet without modification.
            # We will modify Env later. For v3.1 POC, we rely on Env's internal generation or manual override.
            
            env.reset()
            env.target_pos = target
            env.obstacles = obstacles # Inject obstacles
            env.effector_pos = start
            
            total_r = 0
            done = False
            obs = np.array(env._get_obs())
            
            while not done:
                action = policy.predict(obs)
                obs_list, r, done, info = env.step(action.tolist())
                obs = np.array(obs_list)
                total_r += r
                if info.get('collision'):
                    # done is True on collision
                    pass
                    
            rewards.append(total_r)
            if total_r < 0: # Arbitrary failure threshold (collision is -10)
                failures += 1
                
        variance = float(np.var(rewards))
        success_rate = 1.0 - (failures / runs)
        
        result = {
            "reward_variance": variance,
            "success_rate": success_rate,
            "stability_score": 1.0 / (1.0 + variance) # Higher is better
        }
        logger.info(f"Stability Analysis (Diff {difficulty}): {result}")
        return result

stability_evaluator = StabilityEvaluator()
