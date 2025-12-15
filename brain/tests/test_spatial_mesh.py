
import pytest
import numpy as np
from brain.spatial.spatial_mesh import SpatialMesh

def test_mesh_update():
    sm = SpatialMesh()
    rgb = np.zeros((100, 100, 3))
    # Gradient depth: top 0, bottom 1
    y = np.linspace(0, 1, 100)
    depth = np.tile(y[:, np.newaxis], (1, 100))
    
    sm.update_from_depth(rgb, depth)
    assert len(sm.points) > 0 # Should find points > 0.7

def test_clustering():
    sm = SpatialMesh()
    # Manually inject points
    sm.points = [(0,0,1), (0.1,0.1,1), (-0.1,-0.1,1)]
    clusters = sm.get_clusters()
    
    assert len(clusters) == 1
    assert clusters[0].depth_mean == 1.0
