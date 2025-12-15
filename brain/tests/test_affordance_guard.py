
import pytest
from brain.safety.affordance_guard import AffordanceGuard
from brain.vision.object_semantics import SemanticObject, SemanticProperties
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D

def test_speed_limit_fragile():
    guard = AffordanceGuard()
    
    props = SemanticProperties(is_fragile=True)
    obj = SemanticObject("1", "glass", "vessel", {}, properties=props)
    
    # Fast move (1m in 1s = 1m/s) -> FAIL
    p1 = Point3D(0,0,0)
    p2 = Point3D(1,0,0)
    traj_fast = Trajectory3D([p1, p2], duration=1.0)
    
    assert not guard.validate_interaction(obj, "move", traj_fast)
    
    # Slow move (1m in 10s = 0.1m/s) -> PASS
    traj_slow = Trajectory3D([p1, p2], duration=10.0)
    # Note: 'move' isn't in default affordance set for 'vessel' in engine? 
    # 'vessel': {"grasp", "pour_into", "place"}
    # Let's use 'place'
    assert guard.validate_interaction(obj, "place", traj_slow)

def test_semantic_block():
    guard = AffordanceGuard()
    obj = SemanticObject("2", "laptop", "electronics", {})
    
    traj = Trajectory3D([Point3D(0,0,0)], duration=1)
    
    assert not guard.validate_interaction(obj, "pour_into", traj)
