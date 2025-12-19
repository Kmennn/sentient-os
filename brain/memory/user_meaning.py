from dataclasses import dataclass, asdict
import time

@dataclass
class UserMeaning:
    signal_domain: str
    relevance_score: float = 0.5 # Start neutral
    interaction_count: int = 0
    last_interaction_ts: float = 0.0
    
    def to_dict(self):
        return asdict(self)
