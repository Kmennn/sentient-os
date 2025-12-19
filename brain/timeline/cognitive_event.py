from dataclasses import dataclass, asdict
from typing import Optional
import time

@dataclass
class CognitiveEvent:
    timestamp: float
    source: str         # "External", "Internal", "User"
    agent: str          # "Observer", "Analyst", "Governor", "System"
    event_type: str     # "Signal", "Filter", "Reflection", "Adjustment", "Conflict"
    summary: str        # Human readable description
    reference_id: str   # Ledger ID, Signal ID, or Conflict ID
    
    def to_dict(self):
        return asdict(self)
