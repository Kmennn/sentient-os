
import pytest
import time
import threading
from brain.manipulation.replanner import Replanner
from brain.manipulation.manipulation_planner_v2 import Trajectory3D, Point3D
from brain.spatial.spatial_mapper import spatial_mapper

def test_replanner_safe_run(caplog):
    rp = Replanner()
    spatial_mapper.voxel_map.grid.fill(0)
    traj = Trajectory3D(points=[Point3D(0,0,0), Point3D(0.1,0.1,0.1)], duration=0.1)
    
    rp.execute_with_monitoring(traj)
    # Should complete without E-Stop
    assert "E-STOP Triggered" not in caplog.text

def test_replanner_collision_interrupt(caplog):
    import logging
    caplog.set_level(logging.INFO)
    rp = Replanner()
    spatial_mapper.voxel_map.grid.fill(0)
    
    # Long path (more steps)
    # Path within bounds (0.0 to 0.4)
    points = [Point3D(i*0.02, i*0.02, 0.0) for i in range(20)]
    traj = Trajectory3D(points=points, duration=2.0)
    
    # Inject obstacle mid-run
    def inject_obstacle():
        time.sleep(0.1)
        # Block at index 10: 0.2, 0.2, 0.0
        spatial_mapper.voxel_map.mark_occupied(0.2, 0.2, 0.0)
        
    threading.Thread(target=inject_obstacle).start()
    
    rp.execute_with_monitoring(traj)
    
    assert "DYNAMIC COLLISION" in caplog.text
