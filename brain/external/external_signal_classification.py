from enum import Enum

class SignalDomain(Enum):
    SECURITY = "security"
    SYSTEM = "system"
    PRODUCTIVITY = "productivity"
    SOCIAL = "social"
    INFO = "info"
    UNKNOWN = "unknown"

class SignalRiskLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
