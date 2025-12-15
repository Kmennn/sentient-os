
import pytest
import math
from brain.skills.frame_alignment import FrameAligner
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

def test_pure_translation():
    fa = FrameAligner()
    # Skill: Move 1m in X
    points = [Point3D(0,0,0), Point3D(1,0,0)]
    traj = Trajectory3D(points=points, duration=1.0)
    
    # Target: At (10, 10, 0), No rotation
    target = {"x": 10, "y": 10, "z": 0, "orientation": {"yaw": 0}}
    
    aligned = fa.align_trajectory(traj, target)
    
    # Check start
    assert aligned.points[0].x == 10
    assert aligned.points[0].y == 10
    
    # Check end (11, 10, 0)
    assert aligned.points[1].x == 11
    assert aligned.points[1].y == 10

def test_rotation_90deg():
    fa = FrameAligner()
    # Skill: Move 1m in X
    points = [Point3D(0,0,0), Point3D(1,0,0)]
    traj = Trajectory3D(points=points, duration=1.0)
    
    # Target: Rotation 90 deg (pi/2)
    target = {"x": 0, "y": 0, "z": 0, "orientation": {"yaw": math.pi/2}}
    
    aligned = fa.align_trajectory(traj, target)
    
    # End point should be (0, 1) approx
    assert abs(aligned.points[1].x) < 0.001
    assert abs(aligned.points[1].y - 1.0) < 0.001
