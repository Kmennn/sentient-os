import time
from collections import deque
from typing import Deque, List, Optional
import uuid
from brain.reflection.reflection_event import ReflectionEvent, ReflectionEventType
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType, AutonomyDecision

class ReflectionEngine:
    def __init__(self, ledger: AutonomyLedger):
        self.ledger = ledger
        self.event_buffer: Deque[ReflectionEvent] = deque(maxlen=100)
        self.insights: List[str] = []
        self.last_reflection_signal: Optional[str] = None
        self.reflection_confidence: float = 0.0
        
    def process_event(self, event: ReflectionEvent):
        self.event_buffer.append(event)
        self._analyze(event)
        
    def _analyze(self, trigger_event: ReflectionEvent):
        # Time Windows
        SEARCH_CORRELATION_WINDOW = 300 # 5 mins
        DISMISS_CORRELATION_WINDOW = 60 # 1 min
        
        now = trigger_event.timestamp
        
        # Rule 1: Over-Filter Detection (Search after Filter)
        if trigger_event.event_type == ReflectionEventType.USER_MANUAL_SEARCH:
            domain = trigger_event.domain
            # Look for recent filtered alerts in this domain
            for e in reversed(self.event_buffer):
                if e.event_type == ReflectionEventType.ALERT_FILTERED:
                    if e.domain == domain and (now - e.timestamp) < SEARCH_CORRELATION_WINDOW:
                        # Correlation Found!
                        self._log_reflection(
                            DecisionType.REFLECTION_NEGATIVE,
                            f"Over-filtered? User searched for '{domain}' 5 mins after filtering it.",
                            e.domain
                        )
                        return

        # Rule 2: Over-Noise Detection (Dismiss after Show)
        if trigger_event.event_type == ReflectionEventType.ALERT_DISMISSED:
            s_id = trigger_event.item_id
            for e in reversed(self.event_buffer):
                if e.event_type == ReflectionEventType.ALERT_SHOWN:
                    if e.item_id == s_id and (now - e.timestamp) < DISMISS_CORRELATION_WINDOW:
                        self._log_reflection(
                            DecisionType.REFLECTION_NEGATIVE,
                            f"Over-noise? User dismissed '{trigger_event.domain}' immediately.",
                            trigger_event.domain
                        )
                        return

        # Rule 3: Good Signal (Ack after Show)
        if trigger_event.event_type == ReflectionEventType.ALERT_ACKED:
             s_id = trigger_event.item_id
             for e in reversed(self.event_buffer):
                if e.event_type == ReflectionEventType.ALERT_SHOWN:
                    if e.item_id == s_id:
                        self._log_reflection(
                            DecisionType.REFLECTION_POSITIVE,
                            f"Correct? User acknowledged '{trigger_event.domain}'.",
                            trigger_event.domain
                        )
                        return

    def _log_reflection(self, decision_type: DecisionType, reason: str, domain: str):
        decision = AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=decision_type,
            timestamp=time.time(),
            reason=reason,
            was_auto=True
        )
        self.ledger.append(decision)
        
        self.insights.append(f"[{decision_type.value.upper()}] {domain}: {reason}")
        self.last_reflection_signal = decision_type.value
        self.reflection_confidence = 0.8 # Placeholder confidence
