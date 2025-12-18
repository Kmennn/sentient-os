from dataclasses import dataclass, asdict
from enum import Enum
import time
from brain.external.external_signal_classification import SignalDomain, SignalRiskLevel

class SignalSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class ExternalSignal:
    signal_id: str
    source: str
    title: str
    summary: str
    severity: SignalSeverity
    detected_at: float = time.time()
    
    # Classification (v12.0.2)
    domain: SignalDomain = SignalDomain.UNKNOWN
    risk_level: SignalRiskLevel = SignalRiskLevel.NONE
    confidence: float = 0.0
    classified_at: float = 0.0

    def to_dict(self):
        d = asdict(self)
        d['severity'] = self.severity.value
        d['domain'] = self.domain.value
        d['risk_level'] = self.risk_level.value
        return d
