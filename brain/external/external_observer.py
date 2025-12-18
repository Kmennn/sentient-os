from typing import List
import uuid
import time
from brain.external.external_signal import ExternalSignal, SignalSeverity
from brain.external.external_signal_classifier import ExternalSignalClassifier

class ExternalObserver:
    def __init__(self):
        self._signals: List[ExternalSignal] = []
        self._last_check = 0
        self._check_interval = 60 # Check every 60s
        
        self.classifier = ExternalSignalClassifier()
        
        # Mock source for verification
        self.mock_queue: List[ExternalSignal] = []

    def tick(self) -> List[ExternalSignal]:
        now = time.time()
        # Rate limit
        if now - self._last_check < self._check_interval and not self.mock_queue:
            return []
            
        self._last_check = now
        new_signals = []
        
        # Process Mocks
        if self.mock_queue:
            new_signals.extend(self.mock_queue)
            self.mock_queue = []
            
        # Real fetch would go here (e.g. RSS, API calls)
        
        if new_signals:
            # Classify
            classified_signals = [self.classifier.classify(s) for s in new_signals]
            
            self._signals.extend(classified_signals)
            # Keep only last 50 in memory
            if len(self._signals) > 50:
                self._signals = self._signals[-50:]
            
            return classified_signals
                
        return []

    def get_recent_signals(self, limit=50):
        return sorted(self._signals, key=lambda x: x.detected_at, reverse=True)[:limit]

    def inject_mock_signal(self, title, source="test", severity=SignalSeverity.LOW):
        # Helper for verification script
        sig = ExternalSignal(
            signal_id=str(uuid.uuid4()),
            source=source,
            title=title,
            summary=f"Mock signal detected from {source}",
            severity=severity,
            detected_at=time.time()
        )
        self.mock_queue.append(sig)
