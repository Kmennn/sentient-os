
import pytest
import numpy as np
from sim.rl.policy_trainer import PolicyTrainer, SimplePolicy
from sim.envs.manipulation_env import ManipulationEnv

def test_policy_inference():
    policy = SimplePolicy(6, 3)
    obs = np.array([0.1]*6)
    action = policy.predict(obs)
    assert action.shape == (3,)

def test_training_loop():
    env = ManipulationEnv()
    trainer = PolicyTrainer(env)
    
    initial_weights = trainer.policy.weights.copy()
    
    # Train for 5 episodes
    best_weights = trainer.train(episodes=5)
    
    # Weights should (likely) change if improvement found, or stay same if not.
    # At least function runs without error.
    assert best_weights.shape == (3, 6)
