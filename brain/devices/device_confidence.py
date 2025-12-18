from dataclasses import dataclass
import time

@dataclass
class DeviceConfidence:
    device_id: str
    score: float = 0.5
    last_update_ts: float = 0.0
    decay_rate_per_min: float = 0.02
    
    def __post_init__(self):
        if self.last_update_ts == 0.0:
            self.last_update_ts = time.time()

    def get_current_score(self) -> float:
        """Calculates score based on time elapsed since last update."""
        now = time.time()
        elapsed_mins = (now - self.last_update_ts) / 60.0
        if elapsed_mins <= 0:
            return self.score
            
        decay = elapsed_mins * self.decay_rate_per_min
        return max(0.0, self.score - decay)
        
    def boost_score(self, amount: float = 0.05):
        """Register an interaction => boost score."""
        current = self.get_current_score()
        self.score = min(1.0, current + amount)
        self.last_update_ts = time.time()
