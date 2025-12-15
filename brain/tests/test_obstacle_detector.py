
import pytest
from brain.spatial.obstacle_detector import ObstacleDetector
from brain.spatial.spatial_mapper import spatial_mapper
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

def test_check_safe_path():
    od = ObstacleDetector()
    # Reset map
    spatial_mapper.voxel_map.grid.fill(0)
    
    # Path in empty space
    traj = Trajectory3D(points=[Point3D(0,0,0.5), Point3D(0.5,0.5,0.5)], duration=1)
    safe, pt = od.check_path(traj)
    
    assert safe
    assert pt is None

def test_check_collision():
    od = ObstacleDetector()
    spatial_mapper.voxel_map.grid.fill(0)
    
    # Place obstacle
    spatial_mapper.voxel_map.mark_occupied(0.25, 0.25, 0.5)
    
    # Path passing through
    traj = Trajectory3D(points=[Point3D(0,0,0.5), Point3D(0.25, 0.25, 0.5), Point3D(0.5, 0.5, 0.5)], duration=1)
    safe, pt = od.check_path(traj)
    
    assert not safe
    assert pt is not None
    assert pt.x == 0.25
