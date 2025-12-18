from brain.events.event_types import EventType
from brain.governance.attention_gate import AttentionGateDecision
from brain.context.presence_state import PresenceState
import logging

logger = logging.getLogger(__name__)

class OutputSuppressor:
    """
    Decides whether to suppress outputs based on context and governance.
    """
    def should_suppress(self, event_type: EventType, gate_decision: AttentionGateDecision, presence: PresenceState = PresenceState.ALONE) -> bool:
        """
        Determines if an output should be suppressed based on gate decision and presence.
        """
        # 1. Presence Suppression (v9.0)
        # If in PUBLIC (WITH_OTHERS), stricter rules apply to preserve privacy/social grace.
        if presence == PresenceState.WITH_OTHERS:
             # Suppress personal/proactive outputs unless vital. 
             # Logic is handled partly in Router (downgrading channel), but suppressor can kill it early.
             if event_type in [EventType.COPLAN_PROPOSED, EventType.REFLECTION_TRIGGERED]:
                 return True

        # 2. Attention Gate Suppression
        # Since we have no severity yet, let's DEFAULT TO SILENT for Conditional in v7.7 to be safe.
        if gate_decision in [AttentionGateDecision.SILENT, AttentionGateDecision.CONDITIONAL]:
            # Which events are "Loud"?
            # MISSION_QUEUED: Internal state change, usually fine to stream for debug, 
            # but if it implies "I am starting to work", maybe suppress notification?
            # COPLAN_PROPOSED: Definitely Loud (asks for approval).
            
            if event_type == EventType.COPLAN_PROPOSED:
                return True
                
            # Future: REFLECTION_TRIGGERED, NARRATION_GENERATED
            
            # MISSION_QUEUED / STARTED / COMPLETED are borderline.
            # They are state updates. The UI might show them passively.
            # "User-facing outputs" usually means PROACTIVE Prompts.
            # Let's suppress co-plans for now as the main proactive element.
            pass
            
        return False
