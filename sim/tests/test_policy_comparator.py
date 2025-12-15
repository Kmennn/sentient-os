
import pytest
from sim.rl.policy_comparator import PolicyComparator
from sim.rl.policy_trainer import SimplePolicy

def test_comparison_metrics():
    comp = PolicyComparator()
    policy = SimplePolicy() # Untrained random policy
    
    results = comp.compare(policy, episodes=5)
    
    assert "avg_rl_reward" in results
    assert "planner_collision_rate" in results
    # Random policy likely performs worse (negative reward)
    assert isinstance(results["avg_rl_reward"], float)
