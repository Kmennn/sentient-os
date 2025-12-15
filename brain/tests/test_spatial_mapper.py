
import pytest
import numpy as np
from brain.spatial.spatial_mapper import SpatialMapper

def test_voxel_marking():
    sm = SpatialMapper()
    # Mark origin
    sm.voxel_map.mark_occupied(0, 0, 0)
    assert sm.voxel_map.is_occupied(0, 0, 0)
    assert not sm.voxel_map.is_occupied(0.5, 0.5, 0.5)

def test_map_update():
    sm = SpatialMapper()
    # Mock depth map (all 0.5m)
    depth = np.ones((100, 100)) * 0.5
    pose = {"x": 0, "y": 0, "z": 0}
    
    sm.update(depth, pose)
    
    # Should have marked some voxels
    count = sm.get_occupied_voxels()
    assert count > 0
