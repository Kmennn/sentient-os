
import pytest
from brain.robotics.safety_layer import SafetyLayer
from brain.spatial.spatial_mesh import spatial_mesh
from brain.manipulation.manipulator_v2 import Point3D

def test_safe_move():
    sl = SafetyLayer()
    # Ensure mesh is empty
    spatial_mesh.points = []
    
    target = Point3D(0.5, 0.5, 0.5)
    assert sl.validate_move(target)

def test_collision_detection():
    sl = SafetyLayer()
    # Inject an "object" at (0.2, 0.2, 0.2)
    spatial_mesh.points = [(0,0,0)] # Reset
    # We need to mock get_clusters or inject points that create a cluster
    # Let's mock get_clusters specifically for this test or rely on spatial_mesh logic
    # The spatial_mesh.get_clusters() relies on points existing.
    spatial_mesh.points = [(0.2, 0.2, 0.2)]
    
    # Target right on top of it
    target = Point3D(0.2, 0.2, 0.2)
    assert not sl.validate_move(target)
