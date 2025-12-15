
import math
import random
from typing import Tuple, List, Dict

class ManipulationEnv:
    """
    A lightweight, standalone simulation environment for robotic manipulation.
    Follows a Gym-like API (reset, step).
    """
    def __init__(self):
        self.effector_pos = [0.0, 0.0, 0.0]
        self.target_pos = [0.0, 0.0, 0.0]
        self.obstacles: List[Dict[str, float]] = [] # {x, y, z, r}
        self.max_steps = 100
        self.current_step = 0
        self.bounds = 1.0 # Workspace bounds

    def reset(self, seed: int = None) -> List[float]:
        if seed is not None:
            random.seed(seed)
            
        self.effector_pos = [0.0, 0.0, 0.0]
        # Random target in front/right/up quadrant
        self.target_pos = [
            random.uniform(0.3, 0.8),
            random.uniform(-0.5, 0.5),
            random.uniform(0.0, 0.5)
        ]
        
        # Simple obstacle in between (sometimes)
        self.obstacles = []
        if random.random() > 0.5:
             self.obstacles.append({
                 "x": self.target_pos[0] / 2,
                 "y": self.target_pos[1] / 2,
                 "z": self.target_pos[2] / 2,
                 "r": 0.1
             })
             
        self.current_step = 0
        return self._get_obs()

    def step(self, action: List[float]) -> Tuple[List[float], float, bool, Dict]:
        """
        Action: [dx, dy, dz] (clamped to max speed)
        """
        dt = 0.1
        max_speed = 1.0
        
        dx = max(-max_speed, min(max_speed, action[0])) * dt
        dy = max(-max_speed, min(max_speed, action[1])) * dt
        dz = max(-max_speed, min(max_speed, action[2])) * dt
        
        self.effector_pos[0] += dx
        self.effector_pos[1] += dy
        self.effector_pos[2] += dz
        
        self.current_step += 1
        
        # Check Collision
        collision = False
        for obs in self.obstacles:
            dist = math.sqrt(
                (self.effector_pos[0]-obs['x'])**2 + 
                (self.effector_pos[1]-obs['y'])**2 + 
                (self.effector_pos[2]-obs['z'])**2
            )
            if dist < obs['r'] + 0.05: # radius + effector_radius
                collision = True
                break
        
        # Calculate Reward
        dist_to_target = math.sqrt(
            (self.effector_pos[0]-self.target_pos[0])**2 +
            (self.effector_pos[1]-self.target_pos[1])**2 +
            (self.effector_pos[2]-self.target_pos[2])**2
        )
        
        reward = -dist_to_target # Dense reward
        done = False
        
        if collision:
            reward -= 10.0
            done = True
        elif dist_to_target < 0.05:
            reward += 100.0
            done = True
        elif self.current_step >= self.max_steps:
            done = True
            
        return self._get_obs(), reward, done, {"collision": collision}

    def _get_obs(self) -> List[float]:
        # [ex, ey, ez, tx, ty, tz]
        return self.effector_pos + self.target_pos
