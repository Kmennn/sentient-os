
import pytest
from sim.rl.safety_envelope import SafetyEnvelope

def test_safe_trajectory():
    env = SafetyEnvelope()
    # 0 -> 0.05 (0.5m/s) -> Safe
    traj = [[0,0,0], [0.05, 0, 0], [0.1, 0, 0]]
    assert env.check_safety(traj)

def test_unsafe_velocity():
    env = SafetyEnvelope()
    # 0 -> 0.2 (2.0m/s) -> Unsafe
    traj = [[0,0,0], [0.2, 0, 0]]
    assert not env.check_safety(traj)

def test_floor_collision():
    env = SafetyEnvelope()
    traj = [[0,0,-0.1]]
    assert not env.check_safety(traj)
