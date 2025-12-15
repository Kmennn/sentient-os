
import logging
import random
import numpy as np
from typing import Dict
from sim.envs.manipulation_env import ManipulationEnv
from sim.rl.policy_trainer import SimplePolicy

logger = logging.getLogger(__name__)

class BaselinePlanner:
    """
    Simulated baseline (Move straight to target).
    """
    def plan(self, start, target):
        # 10 steps linear interpolation
        path = []
        for i in range(10):
            t = i / 9.0
            x = start[0] + (target[0] - start[0]) * t
            y = start[1] + (target[1] - start[1]) * t
            z = start[2] + (target[2] - start[2]) * t
            path.append([x, y, z])
        return path

class PolicyComparator:
    """
    Compares RL Policy vs Baseline Planner.
    """
    def compare(self, policy: SimplePolicy, episodes=10) -> Dict[str, float]:
        env = ManipulationEnv()
        rl_rewards = []
        planner_collisions = 0
        
        for _ in range(episodes):
            seed = random.randint(0, 1000)
            
            # 1. RL Run
            env.reset(seed=seed)
            total_r = 0
            done = False
            obs = np.array(env._get_obs()) # Initial obs
            while not done:
                action = policy.predict(obs)
                obs_list, r, done, _ = env.step(action.tolist())
                obs = np.array(obs_list)
                total_r += r
            rl_rewards.append(total_r)
            
            # 2. Baseline Run (Heuristic simulation via stepping env)
            # Actually, baseline planner produces a path. We need to "execute" it in env to see collisions.
            # But the Env 'step' expects actions (delta).
            # We can compute action = goal - current (P-controller).
            obs = env.reset(seed=seed) # Reset SAME seed
            start_pos = env.effector_pos[:]
            target_pos = env.target_pos[:]
            
            planner_done = False
            steps = 0
            collision = False
            
            while not planner_done and steps < 100:
                curr = env.effector_pos
                # P-Control Action to target
                msg_x = target_pos[0] - curr[0]
                msg_y = target_pos[1] - curr[1]
                msg_z = target_pos[2] - curr[2]
                
                # Normalize speed to 10.0 (env max speed is 1.0 * dt? step applies dt=0.1)
                # step limit 1.0. action 10.0 -> max speed.
                action = [msg_x * 10, msg_y * 10, msg_z * 10]
                _, _, d, info = env.step(action)
                if info['collision']:
                    collision = True
                
                if d: planner_done = True
                steps += 1
                
            if collision:
                planner_collisions += 1

        avg_rl = sum(rl_rewards)/len(rl_rewards)
        
        results = {
            "avg_rl_reward": avg_rl,
            "planner_collision_rate": planner_collisions / episodes
        }
        logger.info(f"Comparison Result: {results}")
        return results

policy_comparator = PolicyComparator()
