from enum import StrEnum, auto
from typing import Optional
from brain.intents.intent_context import IntentContext
from brain.intents.attention_state import AttentionState

class AttentionGateDecision(StrEnum):
    ALLOW = auto()       # Output is permitted
    SILENT = auto()      # Output is suppressed (internal only)
    CONDITIONAL = auto() # Output depends on severity (stubs for now)

class AttentionGate:
    """
    Decides whether the system is allowed to SURFACE output to the user
    based on the current Attention Context.
    This does NOT block execution, only visibility/notifications.
    """
    def evaluate(self, context: Optional[IntentContext]) -> AttentionGateDecision:
        if not context:
            # No context implies background/internal -> Silent default
            return AttentionGateDecision.SILENT
            
        if context.attention_state == AttentionState.EXPLICIT:
            return AttentionGateDecision.ALLOW
            
        if context.attention_state == AttentionState.PASSIVE:
            return AttentionGateDecision.SILENT
            
        if context.attention_state == AttentionState.INTERRUPT:
            # Future: Check severity threshold
            return AttentionGateDecision.CONDITIONAL
            
        # Default safety fallback
        return AttentionGateDecision.SILENT
