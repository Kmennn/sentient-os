from dataclasses import dataclass, asdict
from enum import Enum
import time

class ImportanceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ExplicitPreference:
    domain: str
    importance_level: ImportanceLevel
    source: str = "USER"
    updated_at: float = 0.0
    
    def to_dict(self):
        d = asdict(self)
        d['importance_level'] = self.importance_level.value
        return d
