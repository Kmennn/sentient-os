
import pytest
from brain.manipulation.manipulation_planner_v5 import ManipulationPlannerV5
from brain.manipulation.manipulation_planner_v2 import Point3D
from brain.learning.policy_advisor import AdvisorySuggestion

def test_advisory_application():
    planner = ManipulationPlannerV5()
    
    sugg = AdvisorySuggestion("lift_height", 0.1, "Test", "pol1", 1.0)
    
    start = Point3D(0,0,0)
    end = Point3D(1,0,0)
    
    traj = planner.plan_with_advisory(start, end, [sugg])
    
    # Default 0.05 + Delta 0.1 = 0.15
    # First point should be lifted to 0.15 z?
    # Logic: [start, lift_pt, end]. lift_pt z = start.z + H = 0 + 0.15.
    
    assert traj is not None
    assert abs(traj.points[1].z - 0.15) < 0.001
