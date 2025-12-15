
import pytest
from brain.manipulation.manipulation_planner_v4 import ManipulationPlannerV4, Point3D
from brain.manipulation.outcomes.execution_outcome_tracker import outcome_tracker, OutcomeStatus
from brain.spatial.spatial_mapper import spatial_mapper

def test_adaptive_plan(caplog):
    mp = ManipulationPlannerV4()
    spatial_mapper.voxel_map.grid.fill(0)
    
    # 1. Clean run
    start = Point3D(0,0,0.05) # Start safe
    target = Point3D(0.5, 0.5, 0)
    outcome_tracker.history = []
    
    traj = mp.plan_reach(start, target)
    # Check max height
    max_z = max([p.z for p in traj.points])
    # Default clearance is 0.1, target z is 0 (clamped to 0.05). Max z ~ 0.15?
    # Lift height = max(0, 0.05) + 0.1 = 0.15
    assert abs(max_z - 0.15) < 0.01
    
    # 2. Add failures to "right_side" (x > 0)
    for _ in range(5):
        outcome_tracker.record_outcome(OutcomeStatus.COLLISION, "right_side")
        
    # 3. Plan again
    import logging
    caplog.set_level(logging.INFO)
    traj_adaptive = mp.plan_reach(start, target)
    
    # Logic: >50% fail -> 2x clearance (0.2)
    # Lift height = 0.05 + 0.2 = 0.25
    max_z_new = max([p.z for p in traj_adaptive.points])
    assert abs(max_z_new - 0.25) < 0.01
    assert "Adapting lift height" in caplog.text
