
import logging
import math
from typing import Tuple
from brain.spatial.spatial_mesh import spatial_mesh
from brain.manipulation.manipulator_v2 import Point3D

logger = logging.getLogger(__name__)

class SafetyLayer:
    def __init__(self):
        self.forbidden_zones = [] # List of (center, radius) tuples
        self.min_safe_distance = 0.5 # 50cm from centroid
        
    def validate_move(self, target: Point3D) -> bool:
        """
        Check if target is safe.
        """
        # 1. Check Spatial Mesh Clusters (Dynamic Obstacles)
        clusters = spatial_mesh.get_clusters()
        for obj in clusters:
            cx, cy, cz = obj.centroid
            
            # Simple Sphere check
            dist = math.sqrt((target.x - cx)**2 + (target.y - cy)**2 + (target.z - cz)**2)
            
            if dist < 0.1: # Too close to object centroid (collide)
                logger.warning(f"Safety: Target too close to object {obj.id} (dist={dist:.2f})")
                return False
                
        # 2. Check Static Forbidden Zones (e.g., user face if detected)
        # Placeholder for now
        
        return True

safety_layer = SafetyLayer()
