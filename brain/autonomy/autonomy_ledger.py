import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum

class DecisionType(Enum):
    SUGGESTED = "suggested"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    AUTO_EXECUTED = "auto_executed"
    BLOCKED = "blocked"
    EXTERNAL_SIGNAL_DETECTED = "external_signal_detected"
    EXTERNAL_SIGNAL_CLASSIFIED = "external_signal_classified"
    EXTERNAL_SUGGESTION_CREATED = "external_suggestion_created"
    EXTERNAL_SUGGESTION_BLOCKED = "external_suggestion_blocked"
    EMERGENCY_VISIBILITY_GRANTED = "emergency_visibility_granted"
    EMERGENCY_VISIBILITY_DENIED = "emergency_visibility_denied"
    EMERGENCY_ACK_CREATED = "emergency_ack_created"
    EMERGENCY_ACKNOWLEDGED = "emergency_acknowledged"
    EMERGENCY_ESCALATED = "emergency_escalated"
    CONTEXTUAL_SEARCH_PERFORMED = "contextual_search_performed"
    CONTEXTUAL_NARRATION_GENERATED = "contextual_narration_generated"
    CONTEXTUAL_MEMORY_RECORDED = "contextual_memory_recorded" # Keep for back-compat or rename? I'll alias or use new
    CONTEXTUAL_MEMORY_STORED = "contextual_memory_stored"
    CONTEXTUAL_PATTERN_DETECTED = "contextual_pattern_detected"
    CONTEXTUAL_PATTERN_EXPLAINED = "contextual_pattern_explained"
    USER_MEANING_UPDATED = "user_meaning_updated"
    EXPLICIT_PREFERENCE_SET = "explicit_preference_set"
    ALERT_FILTERED_BY_PREFERENCE = "alert_filtered_by_preference"
    ALERT_SHOWN_BY_PREFERENCE = "alert_shown_by_preference"
    REFLECTION_POSITIVE = "reflection_positive"
    REFLECTION_NEGATIVE = "reflection_negative"
    ADJUSTMENT_PROPOSED = "adjustment_proposed"
    ADJUSTMENT_APPROVED = "adjustment_approved"
    ADJUSTMENT_REJECTED = "adjustment_rejected"
    AGENT_DECISION = "agent_decision"
    AGENT_BOUNDARY_VIOLATION = "agent_boundary_violation"
    SYNC_STATE_EXPORTED = "sync_state_exported"
    SYNC_STATE_IMPORT_ATTEMPT = "sync_state_import_attempt"
    SYNC_STATE_REJECTED = "sync_state_rejected"
    SYNC_CONFLICT_DETECTED = "sync_conflict_detected"
    SYNC_CONFLICT_RESOLVED = "sync_conflict_resolved"
    SYNC_CONFLICT_REJECTED = "sync_conflict_rejected"
    ACTION_EXECUTED = "action_executed"
    ACTION_BLOCKED = "action_blocked"
    ACTION_REVERTED = "action_reverted"

@dataclass
class AutonomyDecision:
    decision_id: str
    decision_type: DecisionType
    timestamp: float
    suggestion_id: Optional[str] = None
    action_id: Optional[str] = None
    reason: Optional[str] = None
    trust_score: float = 0.0
    focus_state: str = "unknown"
    presence_state: str = "unknown"
    interrupt_style: str = "unknown"
    device_id: str = "unknown"
    was_auto: bool = False

    def to_dict(self):
        d = asdict(self)
        d['decision_type'] = self.decision_type.value
        return d

    @staticmethod
    def from_dict(d):
        d['decision_type'] = DecisionType(d['decision_type'])
        return AutonomyDecision(**d)

class AutonomyLedger:
    def __init__(self, persistence_path="brain/autonomy/autonomy_ledger.json"):
        self.persistence_path = persistence_path
        self._entries: List[AutonomyDecision] = []
        self._load()

    def append(self, decision: AutonomyDecision):
        self._entries.append(decision)
        self._append_to_file(decision)

    def get_entries(self) -> List[AutonomyDecision]:
        return list(self._entries)

    def _load(self):
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, 'r') as f:
                    data = json.load(f)
                    self._entries = [AutonomyDecision.from_dict(d) for d in data]
            except Exception as e:
                print(f"[LEDGER] Failed to load ledger: {e}")

    def _append_to_file(self, decision: AutonomyDecision):
        try:
            # For simplicity in this v1, we rewrite the whole list or read-append?
            # JSON format implies list. Efficient append to JSON list is hard without reading all.
            # For now, safe rewrite for correctness, assuming low volume.
            # Optimization: Append newline delimited JSON (JSONL) is better for ledgers.
            # But requirements said "append-only" and "load on startup".
            # Let's use standard JSON dump for consistency with other files for now, 
            # but note that read-write cycle is not truly append-only IO.
            
            # Actually, let's just write the whole list.
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, 'w') as f:
                json.dump([d.to_dict() for d in self._entries], f, indent=2)
        except Exception as e:
            print(f"[LEDGER] Failed to persist decision: {e}")
