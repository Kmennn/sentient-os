
import random
from typing import List, Dict, Tuple

class ScenarioGenerator:
    """
    Generates environment configurations based on difficulty level.
    """
    def generate(self, difficulty: int, seed: int = None) -> Tuple[List[float], List[Dict], List[float]]:
        """
        Returns (target_pos, obstacles, start_pos)
        """
        if seed is not None:
            random.seed(seed)
            
        start_pos = [0.0, 0.0, 0.0]
        
        # Difficulty 0: Single object, open space.
        # Difficulty 1: One obstacle.
        # Difficulty 2: Cluttered (3 obstacles).
        # Difficulty 3: Narrow passage.
        
        limit = 0.8
        target_pos = [
            random.uniform(0.3, limit),
            random.uniform(-0.5, 0.5),
            random.uniform(0.0, 0.5)
        ]
        
        obstacles = []
        
        if difficulty >= 1:
            # Add one obstacle between start and target
            mid_x = target_pos[0] / 2
            mid_y = target_pos[1] / 2
            obstacles.append({
                "x": mid_x + random.uniform(-0.1, 0.1),
                "y": mid_y + random.uniform(-0.1, 0.1),
                "z": target_pos[2] / 2,
                "r": 0.15
            })
            
        if difficulty >= 2:
            # Add random obstacles
            for _ in range(2):
                obstacles.append({
                    "x": random.uniform(0.2, limit),
                    "y": random.uniform(-0.5, 0.5),
                    "z": random.uniform(0.0, 0.5),
                    "r": 0.1
                })
                
        if difficulty >= 3:
            # Narrow passage (Two walls)
            # Not fully implemented in simple sphere-obstacle model, 
            # but we can place two spheres close together.
            pass
            
        return target_pos, obstacles, start_pos
