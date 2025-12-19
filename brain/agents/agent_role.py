from enum import Enum

class AgentRole(Enum):
    OBSERVER = "observer"
    ANALYST = "analyst"
    GOVERNOR = "governor"
    SYSTEM = "system" # Fallback/Root
