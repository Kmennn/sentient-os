
import pytest
from brain.manipulation.manipulation_planner_v2 import ManipulationPlannerV2, Point3D

def test_reach_planning():
    mp = ManipulationPlannerV2()
    start = Point3D(0,0,0)
    target = Point3D(0.5, 0.5, 0.0) # On floor
    
    traj = mp.plan_reach(start, target)
    assert traj is not None
    assert len(traj.points) > 10
    
    # Check end point (clamped to safety Z)
    final = traj.points[-1]
    assert final.x == 0.5
    assert final.y == 0.5
    assert final.z >= 0.05 # Safety limit

def test_lift_logic():
    mp = ManipulationPlannerV2()
    start = Point3D(0,0,0)
    target = Point3D(0.5, 0.5, 0.1)
    
    traj = mp.plan_reach(start, target)
    # Check intermediate points go up
    zs = [p.z for p in traj.points]
    max_z = max(zs)
    assert max_z > 0.1 # Should lift above target
