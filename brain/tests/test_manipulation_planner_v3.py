
import pytest
from brain.manipulation.manipulation_planner_v3 import ManipulationPlannerV3
from brain.manipulation.manipulation_planner_v2 import Point3D
from brain.spatial.spatial_mapper import spatial_mapper

def test_safe_plan():
    mp = ManipulationPlannerV3()
    spatial_mapper.voxel_map.grid.fill(0) # Clear map
    
    start = Point3D(0, 0, 0.5)
    target = Point3D(0.5, 0.5, 0.5)
    
    traj = mp.plan_reach(start, target)
    assert traj is not None

def test_blocked_plan():
    mp = ManipulationPlannerV3()
    spatial_mapper.voxel_map.grid.fill(0)
    
    start = Point3D(0, 0, 0.5)
    target = Point3D(0.5, 0.5, 0.5)
    
    # Block the middle
    spatial_mapper.voxel_map.mark_occupied(0.25, 0.25, 0.5)
    # Actually the v2 planner lifts to z+0.1, so it goes to 0.6
    # Let's block 0.6 too
    spatial_mapper.voxel_map.mark_occupied(0.25, 0.25, 0.6)
    
    traj = mp.plan_reach(start, target)
    assert traj is None # Should abort
