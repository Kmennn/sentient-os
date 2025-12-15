
import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DetectedObject:
    id: str
    centroid: Tuple[float, float, float]
    bbox: Tuple[float, float, float, float] # x, y, w, h (2D projection)
    depth_mean: float

class SpatialMesh:
    def __init__(self):
        self.points = [] # List of (x,y,z)
        
    def update_from_depth(self, frame_rgb: np.ndarray, depth_map: np.ndarray):
        """
        Convert depth map to simplified point cloud.
        """
        # For v2.4, we implement a simplified logic:
        # 1. Downsample
        # 2. Threshold "close" points
        # 3. Cluster
        
        try:
            h, w = depth_map.shape
            # Simple threshold: objects closer than 0.8 (where 1.0 is near)
            # In our gradient mock, near=1.0. 
            # Let's assume > 0.7 is "interaction zone"
            
            mask = depth_map > 0.7
            if not np.any(mask):
                self.points = []
                return

            # Get indices of points in interaction zone
            ys, xs = np.where(mask)
            
            # Subsample for performance
            step = 10
            self.points = []
            for i in range(0, len(ys), step):
                y, x = ys[i], xs[i]
                d = depth_map[y, x]
                # Project pixel to 3D (fake intrinsics)
                # z = d, x = (u-cx)*z/fx
                z = d 
                px = (x - w/2) / 100.0 
                py = (y - h/2) / 100.0
                self.points.append((px, py, z))
                
        except Exception as e:
            logger.error(f"Mesh Update Error: {e}")

    def get_clusters(self) -> List[DetectedObject]:
        """
        Return clustered objects.
        """
        if not self.points:
            return []
            
        # Mock clustering: assume one big blob if points exist
        # In v2.5 we use DBSCAN
        
        # Calculate bounding box of all points
        pts = np.array(self.points)
        min_x, min_y = np.min(pts[:, 0]), np.min(pts[:, 1])
        max_x, max_y = np.max(pts[:, 0]), np.max(pts[:, 1])
        mean_z = np.mean(pts[:, 2])
        
        obj = DetectedObject(
            id="obj_1",
            centroid=((min_x+max_x)/2, (min_y+max_y)/2, mean_z),
            bbox=(min_x, min_y, max_x-min_x, max_y-min_y),
            depth_mean=mean_z
        )
        return [obj]

spatial_mesh = SpatialMesh()
