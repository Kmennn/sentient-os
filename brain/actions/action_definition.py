from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class ActionDefinition:
    id: str
    name: str
    description: str
    risk_level: RiskLevel
    reversible: bool
    executor: Callable[[], Any]
