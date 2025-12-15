
import pytest
from brain.manipulation.manipulation_planner import ManipulationPlanner

def test_plan_click():
    mp = ManipulationPlanner()
    traj = mp.plan_action("click", (0, 0), (100, 100))
    
    assert traj.action_type == "click"
    assert len(traj.points) == 11 # 0 to 10
    
    # Check end point
    assert traj.points[-1].x == 100
    assert traj.points[-1].y == 100

def test_plan_drag():
    mp = ManipulationPlanner()
    traj = mp.plan_action("drag", (50, 50), (150, 50))
    assert traj.action_type == "drag"
    assert traj.points[5].y == 50 # Should be straight horizontal line
