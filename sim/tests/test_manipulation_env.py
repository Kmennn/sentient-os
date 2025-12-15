
import pytest
from sim.envs.manipulation_env import ManipulationEnv

def test_reset():
    env = ManipulationEnv()
    obs = env.reset(seed=42)
    assert len(obs) == 6
    assert obs[0] == 0.0 # Effector X start

def test_step_mechanics():
    env = ManipulationEnv()
    env.reset(seed=42)
    
    # Move X
    action = [1.0, 0.0, 0.0]
    obs, reward, done, info = env.step(action)
    
    # dt=0.1, dx=1.0 -> move 0.1
    assert abs(obs[0] - 0.1) < 0.001
    assert not done

def test_collision():
    env = ManipulationEnv()
    obs = env.reset(seed=42)
    
    # Manually place obstacle at (0.1, 0, 0)
    env.obstacles = [{"x": 0.1, "y": 0, "z": 0, "r": 0.05}]
    
    # Move into it
    action = [1.0, 0.0, 0.0]
    obs, reward, done, info = env.step(action) # Move to 0.1
    
    assert info['collision']
    assert done
    assert reward < -10.0
