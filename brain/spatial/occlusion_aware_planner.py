
import logging
import math
import heapq
from typing import List, Tuple, Set, Optional
from brain.manipulation.manipulator_v2 import Point3D

logger = logging.getLogger(__name__)

class OcclusionAwarePlanner:
    """
    3D A* Planner for voxel grids to avoid obstacles.
    """
    def __init__(self, resolution=0.05, bounds=(2.0, 2.0, 2.0)):
        self.resolution = resolution
        self.bounds = bounds # +/- x, +/- y, 0 to +z
        self.obstacles: Set[Tuple[int, int, int]] = set()

    def add_obstacle(self, center: Point3D, radius: float):
        """
        Mark voxels as occupied.
        """
        cx, cy, cz = self._to_grid(center)
        r_grid = int(radius / self.resolution)
        
        for x in range(cx - r_grid, cx + r_grid + 1):
            for y in range(cy - r_grid, cy + r_grid + 1):
                 for z in range(cz - r_grid, cz + r_grid + 1):
                     if (x-cx)**2 + (y-cy)**2 + (z-cz)**2 <= r_grid**2:
                         self.obstacles.add((x, y, z))

    def plan_path(self, start: Point3D, end: Point3D) -> Optional[List[Point3D]]:
        """
        A* Search.
        """
        start_node = self._to_grid(start)
        end_node = self._to_grid(end)
        
        if start_node in self.obstacles:
            logger.warning("Start point is occluded!")
            return None
        if end_node in self.obstacles:
            logger.warning("End point is occluded!")
            return None
            
        open_set = []
        heapq.heappush(open_set, (0, start_node))
        came_from = {}
        g_score = {start_node: 0}
        f_score = {start_node: self._heuristic(start_node, end_node)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end_node:
                return self._reconstruct_path(came_from, current)
                
            for neighbor in self._get_neighbors(current):
                if neighbor in self.obstacles:
                    continue
                    
                tentative_g = g_score[current] + 1 # Distance 1
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self._heuristic(neighbor, end_node)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))
                    
        logger.warning("No path found (Occluded).")
        return None

    def _to_grid(self, pt: Point3D) -> Tuple[int, int, int]:
        return (
            int(pt.x / self.resolution),
            int(pt.y / self.resolution),
            int(pt.z / self.resolution)
        )
        
    def _from_grid(self, grid_pt: Tuple[int, int, int]) -> Point3D:
        return Point3D(
            grid_pt[0] * self.resolution,
            grid_pt[1] * self.resolution,
            grid_pt[2] * self.resolution
        )

    def _heuristic(self, a, b):
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

    def _get_neighbors(self, node):
        x, y, z = node
        # 6-connectivity
        moves = [
            (x+1, y, z), (x-1, y, z),
            (x, y+1, z), (x, y-1, z),
            (x, y, z+1), (x, y, z-1)
        ]
        return moves

    def _reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(self._from_grid(current))
            current = came_from[current]
        path.append(self._from_grid(current)) # Start
        path.reverse()
        return path

occlusion_planner = OcclusionAwarePlanner()
