
import pytest
from brain.manipulation.manipulator_v2 import ManipulatorV2, Point3D

def test_trajectory_planning():
    man = ManipulatorV2()
    start = Point3D(0,0,0)
    end = Point3D(1,1,1)
    
    traj = man.plan_trajectory(start, end, steps=10)
    assert len(traj.points) == 11
    assert traj.points[-1].x == 1.0

def test_execution_valid():
    man = ManipulatorV2()
    target = Point3D(0.5, 0.5, 0.2)
    # Distance approx 0.73 < 1.0
    success = man.execute_move(target)
    assert success

def test_execution_out_of_reach():
    man = ManipulatorV2()
    target = Point3D(2.0, 0.0, 0.0) # > 1.0m
    success = man.execute_move(target)
    assert not success
