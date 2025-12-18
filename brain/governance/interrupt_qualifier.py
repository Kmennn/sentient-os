from dataclasses import dataclass
from typing import Optional
from brain.intents.interrupt_reason import InterruptReason

@dataclass
class InterruptDecision:
    qualified: bool
    decision_reason: str

class InterruptQualifier:
    """
    Decides if a proposed interruption has sufficient justification 
    to break the Attention Gate's silence.
    """
    def qualify(self, reason: Optional[InterruptReason]) -> InterruptDecision:
        if not reason:
            return InterruptDecision(False, "No reason provided")
            
        if reason == InterruptReason.SAFETY:
            return InterruptDecision(True, "Approved: Safety Risk")
            
        # Strict v7.8 rules: Only SAFETY interrupts bypassed.
        if reason in [InterruptReason.DEADLINE_RISK, InterruptReason.USER_DEPENDENCY, InterruptReason.OPTIMIZATION]:
             return InterruptDecision(False, f"Deferred: {reason} does not meet Safety threshold")
             
        return InterruptDecision(False, "Unknown reason")
