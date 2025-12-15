
import pytest
from brain.safety.physical_safety_guard import PhysicalSafetyGuard
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D
from brain.robotics.execution_mode import execution_manager, Mode

def test_hard_constraints():
    guard = PhysicalSafetyGuard()
    
    # Safe Plan
    points = [Point3D(0,0,0.1), Point3D(0.1,0.1,0.1)]
    traj = Trajectory3D(points=points, duration=1.0)
    assert guard.verify_plan(traj)
    
    # Floor Violation
    points_bad = [Point3D(0,0,-0.1)]
    traj_bad = Trajectory3D(points=points_bad, duration=1.0)
    assert not guard.verify_plan(traj_bad)

def test_live_speed_limit():
    guard = PhysicalSafetyGuard()
    execution_manager.set_mode("LIVE")
    
    # Fast move: 1 meter in 0.1s = 10m/s -> Unsafe
    points = [Point3D(0,0,0), Point3D(1,0,0)]
    traj = Trajectory3D(points=points, duration=0.1)
    
    assert not guard.verify_plan(traj)
