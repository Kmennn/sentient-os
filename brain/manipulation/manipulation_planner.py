
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Trajectory:
    action_type: str
    points: List[Point]
    duration_ms: int

class ManipulationPlanner:
    def __init__(self):
        pass
        
    def plan_action(self, action_type: str, start: Tuple[int, int], target: Tuple[int, int]) -> Trajectory:
        """
        Generate a trajectory for an action.
        """
        path = []
        steps = 10
        
        # Linear interpolation for now
        dx = (target[0] - start[0]) / steps
        dy = (target[1] - start[1]) / steps
        
        for i in range(steps + 1):
            path.append(Point(
                x=int(start[0] + dx * i),
                y=int(start[1] + dy * i)
            ))
            
        logger.info(f"MPL: Planned {action_type} from {start} to {target}")
        
        return Trajectory(
            action_type=action_type,
            points=path,
            duration_ms=500
        )

manipulation_planner = ManipulationPlanner()
