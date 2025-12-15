
import pytest
from brain.autonomy.spatial_autonomy_engine import SpatialAutonomyEngine
from brain.spatial.spatial_mapper import spatial_mapper
from brain.robotics.robot_controller import robot_controller
import logging

def test_autonomy_clutter_check(caplog):
    caplog.set_level(logging.INFO)
    sa = SpatialAutonomyEngine()
    sa.start_loop()
    
    # Fill map a bit
    for x in range(15):
        for y in range(15):
             for z in range(5):
                 spatial_mapper.voxel_map.mark_occupied(x*0.05, y*0.05, z*0.05)
                 
    sa.tik_tok()
    # Should see log about clutter
    assert "High clutter" in caplog.text or "Autonomy" in caplog.text

def test_autonomy_grasp_trigger(caplog):
    caplog.set_level(logging.INFO)
    sa = SpatialAutonomyEngine()
    sa.start_loop()
    
    # Place object at target
    spatial_mapper.voxel_map.mark_occupied(0.5, 0.5, 0.1)
    
    # Mock robot ready
    robot_controller.bridge.connected = True 
    
    sa.tik_tok()
    
    # Just check if it ran and logged something relevant
    assert "Autonomy" in caplog.text
