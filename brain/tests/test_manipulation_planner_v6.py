
import pytest
from brain.manipulation.manipulation_planner_v6 import ManipulationPlannerV6
from brain.manipulation.manipulation_planner_v2 import Point3D
from brain.learning.policy_advisor import AdvisorySuggestion

def test_hybrid_planning_blending():
    planner = ManipulationPlannerV6()
    planner.set_alpha(0.5) # 50/50
    
    start = Point3D(0,0,0)
    end = Point3D(1,0,0)
    
    # Suggestion: +0.2m lift
    sugg = AdvisorySuggestion("lift_height", 0.2, "Reason", "pol", 1.0)
    
    traj = planner.plan_hybrid(start, end, [sugg])
    
    # Base 0.05. Delta 0.2. Alpha 0.5.
    # Final = 0.05 + 0.2*0.5 = 0.15
    # Lift Pt Z = 0 + 0.15 = 0.15
    assert abs(traj.points[1].z - 0.15) < 0.001

def test_hybrid_fallback_instability():
    planner = ManipulationPlannerV6()
    planner.set_alpha(0.0) # Full Policy
    
    # Force instability
    planner.monitor.variance_threshold = 0.0
    planner.monitor.record_observation(1)
    planner.monitor.record_observation(2)
    
    start = Point3D(0,0,0)
    end = Point3D(1,0,0)
    sugg = AdvisorySuggestion("lift_height", 0.2, "Reason", "pol", 1.0)
    
    traj = planner.plan_hybrid(start, end, [sugg])
    
    # Fallback to Alpha 1.0 -> 0.05
    assert abs(traj.points[1].z - 0.05) < 0.001
