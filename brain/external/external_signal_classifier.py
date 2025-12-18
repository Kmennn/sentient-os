import time
from brain.external.external_signal import ExternalSignal, SignalSeverity
from brain.external.external_signal_classification import SignalDomain, SignalRiskLevel

class ExternalSignalClassifier:
    def classify(self, signal: ExternalSignal) -> ExternalSignal:
        """
        Enriches the signal with Domain and Risk Level based on deterministic rules.
        """
        txt = (signal.title + " " + signal.summary + " " + signal.source).lower()
        
        # Default
        domain = SignalDomain.INFO
        risk = SignalRiskLevel.LOW
        conf = 0.5
        
        # Rule 1: Security
        if any(w in txt for w in ["security", "breach", "hack", "vulnerability", "alert", "cve"]):
            domain = SignalDomain.SECURITY
            risk = SignalRiskLevel.HIGH
            conf = 0.9
            if "critical" in txt or signal.severity == SignalSeverity.HIGH:
                 risk = SignalRiskLevel.CRITICAL
                 conf = 0.95

        # Rule 2: System
        elif any(w in txt for w in ["cpu", "memory", "disk", "crash", "outage", "maintenance", "update"]):
            domain = SignalDomain.SYSTEM
            risk = SignalRiskLevel.MEDIUM
            conf = 0.8
            if signal.severity == SignalSeverity.HIGH:
                risk = SignalRiskLevel.HIGH
        
        # Rule 3: Productivity
        elif any(w in txt for w in ["meeting", "calendar", "deadline", "todo", "email"]):
            domain = SignalDomain.PRODUCTIVITY
            risk = SignalRiskLevel.LOW
            conf = 0.85
            if "urgent" in txt:
                risk = SignalRiskLevel.MEDIUM
                
        # Rule 4: Source based overrides
        if signal.source == "security_feed":
            domain = SignalDomain.SECURITY
            if risk == SignalRiskLevel.LOW:
                risk = SignalRiskLevel.MEDIUM
            conf = 0.99

        # Apply
        signal.domain = domain
        signal.risk_level = risk
        signal.confidence = conf
        signal.classified_at = time.time()
        
        return signal
