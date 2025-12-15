
import logging
import numpy as np
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)

class VoxelGrid:
    def __init__(self, size=(20, 20, 20), resolution=0.05):
        # 20x20x20 grid, 5cm resolution -> 1m x 1m x 1m volume
        self.size = size
        self.resolution = resolution
        self.grid = np.zeros(size, dtype=np.uint8) # 0=Free, 1=Occupied
        
    def mark_occupied(self, x, y, z):
        ix = int(x / self.resolution) + self.size[0]//2
        iy = int(y / self.resolution) + self.size[1]//2
        iz = int(z / self.resolution)
        
        if 0 <= ix < self.size[0] and 0 <= iy < self.size[1] and 0 <= iz < self.size[2]:
            self.grid[ix, iy, iz] = 1

    def is_occupied(self, x, y, z):
        ix = int(x / self.resolution) + self.size[0]//2
        iy = int(y / self.resolution) + self.size[1]//2
        iz = int(z / self.resolution)
        
        if 0 <= ix < self.size[0] and 0 <= iy < self.size[1] and 0 <= iz < self.size[2]:
            return self.grid[ix, iy, iz] == 1
        return False

class SpatialMapper:
    """
    Builds a 3D Voxel map from Depth.
    """
    def __init__(self):
        self.voxel_map = VoxelGrid()
        
    def update(self, depth_map: np.ndarray, pose: Dict[str, float]):
        """
        Project depth pixels to 3D and update voxel map.
        Pose is robot/camera pose {x,y,z, yaw}.
        """
        h, w = depth_map.shape
        # Subsample
        step = 10
        
        # Camera intrinsics (Mock)
        fx, fy = 300, 300
        cx, cy = w/2, h/2
        
        for v in range(0, h, step):
            for u in range(0, w, step):
                d = depth_map[v, u]
                if d > 0.1 and d < 1.0: # Valid depth range
                    # Back-project
                    # z = d (if d is metric)
                    # x = (u - cx) * z / fx
                    # y = (v - cy) * z / fy
                    
                    # In our mock: d is metric-ish (0..1m)
                    z = float(d) # ensure float for math
                    x = (u - cx) * z / fx
                    y = (v - cy) * z / fy
                    
                    # Transform by Pose (Simple translation for now)
                    wx = x + pose.get("x", 0)
                    wy = y + pose.get("y", 0)
                    wz = z + pose.get("z", 0)
                    
                    self.voxel_map.mark_occupied(wx, wy, wz)

    def get_occupied_voxels(self) -> int:
        return np.sum(self.voxel_map.grid)

spatial_mapper = SpatialMapper()
