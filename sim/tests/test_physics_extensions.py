
import pytest
from sim.envs.physics_extensions import PhysicsEngine

def test_kinematic_mode():
    phys = PhysicsEngine(use_physics=False)
    # Start 0, target vel 1.0. dt=0.1.
    # Should move 0.1 immediately.
    new_pos, _ = phys.apply_dynamics([0,0,0], [1.0, 0, 0])
    assert abs(new_pos[0] - 0.1) < 0.001

def test_acceleration_limit():
    phys = PhysicsEngine(use_physics=True)
    phys.max_acceleration = 1.0 # m/s^2. dt=0.1. Max deltaV = 0.1.
    
    # Start rest. Target 10.0 m/s.
    # Should only increase velocity by 0.1.
    # Pos change = 0.1 * dt approx? No, V_new = 0.1. Pos += 0.1*0.1 = 0.01.
    
    new_pos, new_vel = phys.apply_dynamics([0,0,0], [10.0, 0, 0])
    
    assert abs(new_vel[0] - 0.1) < 0.001
    assert abs(new_pos[0] - 0.01) < 0.001 

def test_inertia():
    phys = PhysicsEngine(use_physics=True)
    phys.current_velocity = [1.0, 0, 0]
    phys.max_acceleration = 1.0 
    
    # Target 0 (Stop).
    # Delta needed -1.0. Max delta -0.1.
    # New Vel = 0.9.
    
    new_pos, new_vel = phys.apply_dynamics([0,0,0], [0,0,0])
    assert abs(new_vel[0] - 0.9) < 0.001
    # It takes time to stop.
