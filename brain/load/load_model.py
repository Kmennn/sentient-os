from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any

class LoadLevel(Enum):
    LOW = auto()
    MED = auto()
    HIGH = auto()

@dataclass
class LoadSnapshot:
    """
    Represents the estimated cognitive load for a specific day.
    """
    date_str: str
    level: LoadLevel
    score: int # 0-100
    density_label: str # e.g. "Low density", "High congestion"
    details: List[str] = field(default_factory=list)
