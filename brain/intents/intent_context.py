from dataclasses import dataclass
from typing import Optional
import time
import uuid
from brain.presence.client import ClientType

from brain.intents.interaction_modality import InteractionModality
from brain.intents.attention_state import AttentionState
from brain.intents.interrupt_reason import InterruptReason

@dataclass
class IntentContext:
    intent_id: str
    source_client_id: str
    source_client_type: ClientType
    received_at: float
    modality: InteractionModality = InteractionModality.BACKGROUND
    attention_state: AttentionState = AttentionState.PASSIVE
    interrupt_reason: Optional[InterruptReason] = None
    
    @staticmethod
    def create(client_id: str, client_type: ClientType, modality: InteractionModality = InteractionModality.BACKGROUND, attention_state: AttentionState = AttentionState.PASSIVE, interrupt_reason: Optional[InterruptReason] = None):
        if attention_state == AttentionState.INTERRUPT and not interrupt_reason:
            # Enforce reason for interrupts
            # In a real system, might raise Error. For now, log/fallback?
            # Let's simple allow None, but Qualifier will reject it. 
            pass
            
        return IntentContext(
            intent_id=str(uuid.uuid4()),
            source_client_id=client_id,
            source_client_type=client_type,
            received_at=time.time(),
            modality=modality,
            attention_state=attention_state,
            interrupt_reason=interrupt_reason
        )
