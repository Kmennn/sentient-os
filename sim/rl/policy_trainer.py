
import logging
import random
import numpy as np # Minimal dependency
from sim.envs.manipulation_env import ManipulationEnv

logger = logging.getLogger(__name__)

class SimplePolicy:
    def __init__(self, input_dim=6, output_dim=3):
        # Linear layer: Output = W * Input
        self.weights = np.random.randn(output_dim, input_dim) * 0.1
    
    def predict(self, obs):
        return np.dot(self.weights, obs)

class PolicyTrainer:
    """
    Trains a policy using Hill Climbing (Simulated Optimization).
    Safe, Deterministic, No heavy DL deps.
    """
    def __init__(self, env: ManipulationEnv):
        self.env = env
        self.policy = SimplePolicy()
        self.best_reward = -float('inf')
        self.best_weights = self.policy.weights.copy()
    
    def train(self, episodes=100):
        logger.info(f"Starting Training ({episodes} episodes)...")
        
        for ep in range(episodes):
            # Mutate weights
            noise = np.random.randn(*self.policy.weights.shape) * 0.05
            candidate_weights = self.best_weights + noise
            self.policy.weights = candidate_weights
            
            # Evaluate
            total_reward = self._evaluate_episode()
            
            # Accept if better
            if total_reward > self.best_reward:
                self.best_reward = total_reward
                self.best_weights = candidate_weights.copy()
                logger.info(f"Ep {ep}: New Best Reward {self.best_reward:.2f}")
            else:
                # Revert
                self.policy.weights = self.best_weights
        
        logger.info("Training Complete.")
        return self.best_weights

    def _evaluate_episode(self):
        obs = self.env.reset(seed=random.randint(0, 1000))
        total_reward = 0
        done = False
        obs = np.array(obs)
        
        while not done:
            action = self.policy.predict(obs)
            obs_list, reward, done, _ = self.env.step(action.tolist())
            obs = np.array(obs_list)
            total_reward += reward
        return total_reward

policy_trainer = PolicyTrainer(ManipulationEnv())
