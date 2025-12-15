
import pytest
from brain.manipulation.trajectory_smoother import TrajectorySmoother
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

def test_smoothing_averaging():
    smoother = TrajectorySmoother()
    # zig-zag
    points = [
        Point3D(0,0,0),
        Point3D(0.5, 1.0, 0), # outlier high
        Point3D(1.0, 0, 0)
    ]
    traj = Trajectory3D(points, 2.0)
    
    smoothed = smoother.smooth(traj)
    
    mid = smoothed.points[1]
    # Average Y = (0 + 1 + 0) / 3 = 0.33
    assert abs(mid.y - 0.33) < 0.01
    
    # Endpoints fixed
    assert smoothed.points[0].x == 0
    assert smoothed.points[2].x == 1.0
