from dataclasses import dataclass
from enum import Enum

class ActionRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class ActionCapability:
    action_id: str
    description: str
    risk_level: ActionRisk
    reversible: bool
    requires_consent: bool
