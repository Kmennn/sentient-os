
import pytest
from sim.rl.policy_stability import StabilityEvaluator
from sim.rl.policy_trainer import SimplePolicy

def test_stability_metric():
    evaluator = StabilityEvaluator()
    policy = SimplePolicy() 
    
    metrics = evaluator.evaluate(policy, difficulty=0, runs=5)
    
    assert "reward_variance" in metrics
    assert "success_rate" in metrics
    assert metrics["success_rate"] >= 0.0 and metrics["success_rate"] <= 1.0
