from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class MissionModel(BaseModel):
    mission_id: str
    priority: int
    started_at: float
    payload: Optional[str] = None

class QueueItem(BaseModel):
    mission_id: str
    priority: int
    blocked_until: float

class SystemState(BaseModel):
    tick_time: float
    active_mission: Optional[MissionModel]
    queue: List[QueueItem]
    connected_clients: int = 0
    clients_summary: dict = {}

    last_intent_source_type: Optional[str] = None
    last_intent_modality: Optional[str] = None
    last_intent_attention_state: Optional[str] = None
    last_attention_gate_decision: Optional[str] = None
    last_output_suppressed: bool = False
    last_interrupt_reason: Optional[str] = None
    last_interrupt_decision: Optional[str] = None
    pending_proactive_suggestions: List[Dict[str, Any]] = []
    autonomy_active: bool = False
    # v12.2
    last_emergency_visible: bool = False
    last_emergency_reason: str = ""
    # v12.3
    pending_emergency_count: int = 0
    highest_escalation_level: int = 0
    # v13.1
    last_contextual_narration_available: bool = False
    
    pending_interrupt_requests: List[dict] = []
    interrupt_preference_summary: Dict[str, str] = {}
    interrupt_style: str = "ask_for_important"
    current_window_mode: str = "unknown"
    focus_state: str = "free"
    focus_source: str = "none"
    focus_pattern_proposals: List[dict] = []
    presence_state: str = "unknown"
    presence_source: str = "default"
    audience_mode: str = "neutral"
    tone_profile: str = "neutral"
    last_output_channel: str = "none"
    last_output_targets: List[str] = []
    connected_devices: int = 0
    active_device: str = "none"
    active_device_confidence: float = 0.0
    last_handoff: str = "none"
    has_context_window: bool = False
    context_source_device: str = "none"
    context_expires_in_ms: float = 0.0
    confidence_level: str = "MED"
    device_trust_score: float = 0.5
    device_list: List[dict] = [] # [{id, type, trust, active}]
    # Future: Trust, Pending Proposals, etc.
