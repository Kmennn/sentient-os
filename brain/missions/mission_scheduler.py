# ==========================================
# ⚠️ STABILITY ZONE — FEATURE FROZEN
#
# This file is part of Sentient OS core logic.
# Feature-frozen as of v22.0.0.
#
# Allowed:
# - Bug fixes
# - Refactors without behavior change
#
# Forbidden:
# - New features
# - New decision logic
# - New autonomy paths
#
# All changes must preserve behavior.
# ==========================================

import heapq
import time
import logging
from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import List, Optional, Any

from brain.optimization.mission_optimizer import OptimizationHint, OptimizationAction
from brain.services.scheduler_service import SchedulerService
from brain.services.simulation_service import SimulationService
from brain.services.memory_service import MemoryService
from brain.services.governance_service import GovernanceService
from brain.intents.conflict_detector import ConflictDetector
from brain.governance.conflict_policy import ConflictPolicy, Resolution
from brain.intents.deferral_engine import DeferralEngine, DeferralStrategy
from brain.proactive.suggestion_guard import SuggestionGuard
from brain.proactive.routine_suggester import RoutineSuggester
from brain.intents.intent import Intent, IntentPriority
from brain.intents.temporal_intent import TemporalIntent, TimeFlexibility
from brain.auth.role import UserRole
from brain.missions.mission_contract import MissionContract
from brain.preferences.scheduling_preferences import SchedulingPreferences

from brain.events.event_bus import event_bus
from brain.events.event_types import EventType

logger = logging.getLogger(__name__)

class TickContext:
    def __init__(self, tick_id: str):
        self.tick_id = tick_id
        self.executed_actions = set()
        self.ledger_entries = set()
        self.invariant_violation_count = 0


class BrainPhase(Enum):
    OBSERVE = "observe"
    ANALYZE = "analyze"
    DECIDE = "decide"
    EXECUTE = "execute"
    RECORD = "record"

# S6: Tick Budget Constants
MAX_TICK_DURATION_MS = 100
SLOW_TICK_THRESHOLD_MS = 50

# P3.3: Resource Leak Thresholds
MAX_PENDING_EVENTS = 100
MAX_PENDING_ACTIONS = 10
MAX_QUEUE_SIZE = 50

class MissionPriority(IntEnum):
    BACKGROUND = 1
    SYSTEM = 5
    USER = 10
    CRITICAL = 20

@dataclass(order=True)
class QueuedMission:
    priority: int
    timestamp: float
    mission_id: str = field(compare=False)
    payload: Any = field(compare=False, default=None)
    blocked_until: float = field(compare=False, default=0.0)
    hints: List[OptimizationHint] = field(compare=False, default_factory=list)

from brain.intents.intent_context import IntentContext
from brain.governance.attention_gate import AttentionGate, AttentionGateDecision
from brain.governance.output_suppressor import OutputSuppressor
from brain.governance.interrupt_qualifier import InterruptQualifier
from brain.governance.interrupt_consent_gate import InterruptConsentGate
from brain.ambient.ambient_observer import AmbientObserver
from brain.ambient.ambient_observer import AmbientObserver
from brain.proactive.suggestion_engine import SuggestionEngine
from brain.proactive.proactive_suggestion import SuggestionStatus
from brain.ambient.ambient_observer import AmbientObserver
from brain.proactive.suggestion_engine import SuggestionEngine
from brain.proactive.proactive_suggestion import SuggestionStatus, SuggestionType
from brain.actions.action_registry import ActionRegistry
from brain.autonomy.autonomy_policy import AutonomyPolicy
from brain.autonomy.autonomy_ledger import AutonomyLedger, AutonomyDecision, DecisionType
from brain.external.external_observer import ExternalObserver
from brain.external.external_signal import ExternalSignal
from brain.external.external_signal_classification import SignalRiskLevel
from brain.external.external_suggestion_policy import ExternalSuggestionPolicy
from brain.external.external_suggestion_adapter import ExternalSuggestionAdapter
from brain.external.emergency_visibility_policy import EmergencyVisibilityPolicy
from brain.external.emergency_escalation import EmergencyEscalationManager
from brain.contextual.contextual_search_engine import ContextualSearchEngine
from brain.contextual.contextual_narrator import ContextualNarrator
from brain.memory.contextual_memory import ContextualMemory
from brain.memory.contextual_pattern_analyzer import ContextualPatternAnalyzer
from brain.memory.pattern_narrator import PatternNarrator
from brain.memory.meaning_memory import MeaningMemory, InteractionType
from brain.preferences.preference_store import PreferenceStore, ExplicitPreference, ImportanceLevel
from brain.alerts.alert_importance import AlertImportanceResolver
from brain.reflection.reflection_event import ReflectionEvent, ReflectionEventType
from brain.reflection.reflection_engine import ReflectionEngine
from brain.reflection.adjustment_engine import AdjustmentEngine
from brain.agents.agent_context import AgentContext, AgentRole, OBSERVER_CONTEXT, ANALYST_CONTEXT, GOVERNOR_CONTEXT
from brain.sync.state_exporter import StateExporter
from brain.sync.state_importer import StateImporter
from brain.sync.conflict_resolver import ConflictResolver
from brain.timeline.timeline_builder import TimelineBuilder
from brain.timeline.cognitive_summary import CognitiveSummaryEngine, CognitiveSummary
from brain.timeline.system_confidence import ConfidenceEngine, SystemConfidence, ConfidenceLevel
from brain.actions.action_executor import ActionSandbox
from brain.actions.action_capability import ActionCapability, ActionRisk
from brain.actions.action_result import ActionStatus
from brain.autonomy.autonomy_budget_manager import AutonomyBudgetManager
from brain.autonomy.recovery_manager import RecoveryManager
from brain.autonomy.recovery_state import RecoveryLevel
from brain.autonomy.override_manager import OverrideManager, OverrideScope
from brain.runtime.execution_state_store import ExecutionStateStore, ActionPhase, ExecutionState
from brain.proactive.proactive_suggestion import VisibilityLevel
from brain.intents.interrupt_request import InterruptRequest, InterruptRequestStatus

class MissionScheduler:
    """
    Orchestrator for mission execution.
    Delegates logic to Services.
    """
    def __init__(self):
        self._queue: List[QueuedMission] = []
from brain.memory.interrupt_memory import InterruptMemory
from brain.preferences.user_interrupt_settings import UserInterruptSettings
from brain.preferences.interrupt_style import InterruptStyle
from brain.preferences.user_interrupt_schedule import UserInterruptSchedule
from brain.context.focus_state import FocusState
from brain.context.calendar_focus_provider import CalendarFocusProvider
from brain.context.manual_focus_provider import ManualFocusProvider
from brain.context.focus_resolver import FocusResolver
from brain.learning.focus_pattern_detector import FocusPatternDetector
from brain.learning.focus_pattern_consent import FocusPatternConsent
from brain.context.presence_state import PresenceState
from brain.context.app_presence_provider import AppPresenceProvider
from brain.context.manual_presence_provider import ManualPresenceProvider
from brain.context.presence_resolver import PresenceResolver
from brain.communication.message_adapter import MessageAdapter
from brain.communication.output_router import OutputRouter
from brain.devices.device_registry import DeviceRegistry
from brain.devices.active_device_resolver import ActiveDeviceResolver
from brain.devices.active_device import InteractionType
from brain.context.context_window_manager import ContextWindowManager
from brain.devices.device_confidence_manager import DeviceConfidenceManager
from brain.persistence.device_registry_store import DeviceRegistryStore
from brain.persistence.user_context_store import UserContextStore
from brain.devices.device_handoff import DeviceHandoff
from brain.devices.handoff_detector import HandoffDetector


logger = logging.getLogger(__name__)

class MissionPriority(IntEnum):
    BACKGROUND = 1
    SYSTEM = 5
    USER = 10
    CRITICAL = 20

@dataclass(order=True)
class QueuedMission:
    priority: int
    timestamp: float
    mission_id: str = field(compare=False)
    payload: Any = field(compare=False, default=None)
    blocked_until: float = field(compare=False, default=0.0)
    hints: List[OptimizationHint] = field(compare=False, default_factory=list)

from brain.output.voice_output_manager import VoiceOutputManager
from brain.context.signals.app_context_provider import AppContextProvider
from brain.context.signals.calendar_provider import CalendarProvider
from brain.autonomy.trust_gate import TrustGate

class MissionScheduler:
    """
    Orchestrator for mission execution.
    Delegates logic to Services.
    """
    def __init__(self):
        # ... (Previous init code) ...
        self._queue: List[QueuedMission] = []
        self._active_mission: Optional[QueuedMission] = None
        
        # S3: Phase & Invariant Tracking
        self._current_phase: Optional[BrainPhase] = None
        self._pending_ledger_entries: List[AutonomyDecision] = []
        self._cycle_auto_actions: List[Any] = []
        
        # S4: Crash Safety
        self._startup_blocked: bool = False
        
        # S5: Tick Context (Idempotency)
        self._tick_context: Optional[TickContext] = None
        
        # S6: Tick Budget State
        self._last_tick_duration_ms: float = 0.0
        self._backpressure_active: bool = False
        self._last_state_snapshot: dict = {}
        
        # P3.2: Stall Detection State (edge-triggered)
        self._consecutive_slow_ticks: int = 0
        self._consecutive_healthy_ticks: int = 0
        self._stall_active: bool = False
        
        # P3.3: Resource Leak Detection State (edge-triggered)
        self._leak_suspected: bool = False
        self._pending_actions_count: int = 0
        
        # H4: Voice Output Manager
        self.voice_manager = VoiceOutputManager(self) # access to context via self
        
        # H6: Context Providers (Read-Only)
        self.app_provider = AppContextProvider()
        self.calendar_provider = CalendarProvider()
        self._last_app_context_data = None
        self._last_cal_context_data = None
        
        # H10: Trust Gate
        self.trust_gate = TrustGate()
        
        # Event Bus
        self.event_bus = event_bus
        
        # Context Tracking
        self.last_intent_context: Optional[IntentContext] = None
        self.last_gate_decision: Optional[AttentionGateDecision] = None
        self.last_output_suppressed: bool = False
        
        # Governance & Gates
        self.attention_gate = AttentionGate()
        self.output_suppressor = OutputSuppressor()
        self.interrupt_qualifier = InterruptQualifier()
        
        self.interrupt_memory = InterruptMemory()
        self.consent_gate = InterruptConsentGate(self.interrupt_memory)
        self.user_interrupt_settings = UserInterruptSettings("user_default")
        self.user_interrupt_schedule = UserInterruptSchedule.create_default("user_default")
        
        # Focus Context
        self.manual_focus_provider = ManualFocusProvider()
        self.calendar_focus_provider = CalendarFocusProvider()
        self.focus_resolver = FocusResolver(self.manual_focus_provider, self.calendar_focus_provider)
        
        self.pattern_detector = FocusPatternDetector()
        self.pattern_consent = FocusPatternConsent(self.pattern_detector)
        
        # Presence Context
        self.manual_presence_provider = ManualPresenceProvider()
        self.app_presence_provider = AppPresenceProvider()
        self.presence_resolver = PresenceResolver(self.manual_presence_provider, self.app_presence_provider)

        # User Context (Persistence)
        self.user_context_store = UserContextStore()
        self.user_context = self.user_context_store.load()
        print(f"UserContext loaded (Focus Patterns: {len(self.user_context.focus_patterns)})")
        
        # Hydrate
        # 1. Focus Patterns
        for p_data in self.user_context.focus_patterns:
            p = FocusPattern.from_dict(p_data)
            self.pattern_detector.patterns[p.pattern_id] = p
            
        # 2. Manual Focus
        if self.user_context.manual_focus_expiry:
             # Only restore if in future
             if self.user_context.manual_focus_expiry > time.time():
                 self.manual_focus_provider._focus_expiry = self.user_context.manual_focus_expiry
                 
        # 3. Interrupt Settings
        if self.user_context.interrupt_settings:
            # Replaces default settings
            self.user_interrupt_settings = UserInterruptSettings.from_dict(self.user_context.interrupt_settings)
            
        # 4. Schedule
        if self.user_context.interrupt_schedule:
             self.user_interrupt_schedule = UserInterruptSchedule.from_dict(self.user_context.interrupt_schedule)
             
        # 5. Presence Override
        if self.user_context.presence_override:
             self.manual_presence_provider._override = PresenceState(self.user_context.presence_override)

        # communication
        self.message_adapter = MessageAdapter()
        self.output_router = OutputRouter()
        self.last_output_channel: str = "none" # For State
        self.last_interrupt_reason: Optional[str] = None
        self.last_interrupt_decision: Optional[str] = None
        self.last_output_suppressed: bool = False
        self.pending_interrupts = {}
        
        # Devices (Persistence)
        self.registry_store = DeviceRegistryStore()
        loaded_registry = self.registry_store.load()
        if loaded_registry:
            self.device_registry = loaded_registry
            print(f"DeviceRegistry restored: {len(self.device_registry._devices)} devices.")
        else:
            self.device_registry = DeviceRegistry()
            print("DeviceRegistry initialized (Fresh).")
            
        self.active_device_resolver = ActiveDeviceResolver()
        self.handoff_detector = HandoffDetector()
        self.context_window_manager = ContextWindowManager()
        self.device_confidence_manager = DeviceConfidenceManager(self.device_registry)
        
        self.last_handoff: Optional[DeviceHandoff] = None
        self.last_output_targets: List[str] = []
        
        # Ambient Autonomy (v11)
        self.ambient_observer = AmbientObserver(self)
        self.proactive_engine = SuggestionEngine()
        self.action_registry = ActionRegistry()
        self.autonomy_policy = AutonomyPolicy()
        self.autonomy_ledger = AutonomyLedger()
        
        # v12.0 External 
        self.external_observer = ExternalObserver()
        self.external_policy = ExternalSuggestionPolicy()
        self.external_adapter = ExternalSuggestionAdapter()
        self.emergency_policy = EmergencyVisibilityPolicy()
        self.emergency_manager = EmergencyEscalationManager()
        self.contextual_search = ContextualSearchEngine()
        self.contextual_narrator = ContextualNarrator()
        self.contextual_memory = ContextualMemory()
        self.pattern_analyzer = ContextualPatternAnalyzer(self.contextual_memory)
        self.pattern_narrator = PatternNarrator()
        self.meaning_memory = MeaningMemory()
        self.preference_store = PreferenceStore(self.meaning_memory)
        self.alert_resolver = AlertImportanceResolver(self.preference_store)
        self.reflection_engine = ReflectionEngine(self.autonomy_ledger)
        self.adjustment_engine = AdjustmentEngine(self.preference_store, self.autonomy_ledger)
        self.last_adjustment_check = 0.0
        
        # v17.0
        self.current_agent_phase = AgentRole.SYSTEM.value
        
        # v18.0
        self.state_exporter = StateExporter(self.preference_store, self.meaning_memory, self.autonomy_ledger, self)
        self.conflict_resolver = ConflictResolver(self.preference_store, self.meaning_memory)
        self.state_importer = StateImporter(self.preference_store, self.meaning_memory, self.autonomy_ledger, self.conflict_resolver)
        # v19.0
        self.timeline_builder = TimelineBuilder(self.autonomy_ledger)
        self.last_summary: CognitiveSummary = None
        self.last_summary_time = 0
        self.last_confidence: SystemConfidence = None
        self.action_sandbox = ActionSandbox(self.autonomy_ledger, self)
        self.budget_manager = AutonomyBudgetManager(self.autonomy_ledger)
        self.recovery_manager = RecoveryManager(self.autonomy_ledger)
        self.override_manager = OverrideManager(self.autonomy_ledger)
        self.execution_store = ExecutionStateStore()
        
        # Check for Crash Recovery
        self._check_startup_recovery()
        
        # ... (Services) ...


    # ... (Properties and Setters) ...

    def _enter_phase(self, phase: BrainPhase):
        self._current_phase = phase

    def _assert_phase(self, allowed: List[BrainPhase]):
        if self._current_phase not in allowed:
            raise RuntimeError(
                f"Illegal operation in phase {self._current_phase}. "
                f"Allowed: {allowed}"
            )

    
    def get_confidence_info(self):
        # Return info for the active device
        dev_id, _ = self.active_device_resolver.resolve()
        if not dev_id:
             return 0.5, "MED"
        return self.device_confidence_manager.get_score(dev_id), self.device_confidence_manager.get_level(dev_id)

    def register_device(self, device_id: str, device_type: str, capabilities: List[str]):
        self.device_registry.register_heartbeat(device_id, device_type, capabilities)
        self.registry_store.save(self.device_registry)

    def report_interaction(self, device_id: str, interaction_type: str):
        try:
            prev_dev_id, _ = self.active_device_resolver.resolve()
            
            itype = InteractionType(interaction_type.lower())
            self.active_device_resolver.report_interaction(device_id, itype)
            
            # Update Confidence
            self.device_confidence_manager.register_interaction(device_id)
            
            print(f"Interaction Reported: {device_id} ({itype})")
            
            # Check for Handoff
            new_dev_id, _ = self.active_device_resolver.resolve()
            handoff = self.handoff_detector.check_handoff(prev_dev_id, new_dev_id)
            if handoff:
                print(f"Handoff Detected: {handoff.from_device_id} -> {handoff.to_device_id}")
                self.last_handoff = handoff
                
                # Create Context Window
                payload = {
                    "active_mission_id": self._active_mission.mission_id if self._active_mission else None,
                    "active_mission_name": self._active_mission.description if self._active_mission else None,
                    # Add more state here?
                }
                self.context_window_manager.create_window(prev_dev_id, new_dev_id, payload)
                
                # Determine Handoff Message
                msg = "Continuing here."
                if payload["active_mission_name"]:
                    msg = f"Continuing: {payload['active_mission_name']}"
                
                # Create synthetic event
                event_payload = {
                    "id": f"handoff_{int(time.time())}",
                    "mission_type": "SYSTEM_HANDOFF",
                    "status": "COMPLETED",
                    "message": msg,
                }
                
                # Inject Tone/Audience
                pres_state = self.get_current_presence_state()
                aud, tone = self.get_current_audience_tone() 
                event_payload["audience_mode"] = str(aud.value)
                event_payload["tone_profile"] = str(tone.value)
                
                # Route to NEW device ONLY
                active_devices = self.device_registry.get_active_devices()
                
                # Get confidence for routing
                conf = self.device_confidence_manager.get_score(new_dev_id)
                
                channel, targets = self.output_router.route(
                    pres_state, tone, False, False, active_devices, active_device_id=new_dev_id, device_confidence=conf
                )
                
                event_payload["output_channel"] = str(channel.value)
                event_payload["target_devices"] = targets
                self.last_output_channel = str(channel.value)
                self.last_output_targets = targets
                
                self.event_bus.emit(EventType.MISSION_QUEUED, event_payload)
                
                # Consume window
                self.context_window_manager.consume_window(new_dev_id)
                
                # Consume window
                self.context_window_manager.consume_window(new_dev_id)
                
        except ValueError:
            print(f"Invalid interaction type: {interaction_type}")

    def set_interrupt_style(self, style_str: str):
        try:
            # Need to import InterruptStyle if not top level?
            # It's likely imported or we cast via string if enum supports it.
            # user_interrupt_settings.style expects InterruptStyle enum.
            # I need `from brain.preferences.interrupt_style import InterruptStyle`
            # I'll rely on existing imports or add it.
            # Assuming it's imported or I can use value assignment if it's not typed strictly at runtime
            # But python is typed. `style` field is typed.
            pass 
            # I will assume I need to handle conversion.
            from brain.preferences.interrupt_style import InterruptStyle
            s = InterruptStyle(style_str.lower())
            self.user_interrupt_settings.style = s
            print(f"Interrupt Style set to: {s.value}")
            self.save_user_context()
        except ValueError:
            print(f"Invalid interrupt style: {style_str}")

    def get_active_device_info(self):
        return self.active_device_resolver.resolve()

    def save_user_context(self):
        """Persists current user context to disk."""
        self.user_context_store.save(
            focus_patterns=list(self.pattern_detector.patterns.values()),
            interrupt_settings=self.user_interrupt_settings,
            interrupt_schedule=self.user_interrupt_schedule,
            manual_focus_expiry=self.manual_focus_provider._focus_expiry,
            presence_override=self.manual_presence_provider._override.value if self.manual_presence_provider._override else None
        )
        
    def set_presence_public(self):
        self.manual_presence_provider.set_public()
        print("Presence set to: PUBLIC")

    def set_presence_private(self):
        self.manual_presence_provider.set_private()
        print("Presence set to: PRIVATE")
        self.save_user_context()
        
    def get_summary(self, force_refresh: bool = False) -> CognitiveSummary:
        now = time.time()
        # Refresh every 10 mins (600s) or if forced
        if force_refresh or (now - self.last_summary_time > 600) or self.last_summary is None:
            # Build 24h timeline
            events = self.timeline_builder.build_timeline(duration_seconds=86400)
            self.last_summary = CognitiveSummaryEngine.summarize(events)
            self.last_confidence = ConfidenceEngine.evaluate(events, self.last_confidence)
            self.last_summary_time = now
            
        return self.last_summary

    def get_system_confidence(self) -> SystemConfidence:
        # Ensure we have data
        if self.last_confidence is None:
             self.get_summary() # trigger build
        return self.last_confidence

    def is_safe_to_execute(self, cap: ActionCapability) -> bool:
        # -2. Override Check (v21.2)
        if self.override_manager.has_override(OverrideScope.ACTION):
             print(f"[Scheduler] {cap.action_id}: FORCED EXECUTION (Override Active)")
             
             # Trust Penalty
             penalty = -0.10
             if self.recovery_manager.state.level == "HARD": # String comparison or enum if imported
                  penalty -= 0.10 # Hard recovery forced = -20%
             
             print(f"[Scheduler] Override Penalty: {penalty}")
             self.update_device_trust(penalty)
             
             self.override_manager.use_override(OverrideScope.ACTION, cap.action_id)
             return True

        # -1. Recovery Check (v21.1)
        if self.recovery_manager.is_action_blocked():
             print(f"[Scheduler] Blocked {cap.action_id}: System in Recovery Mode.")
             # Log implicitly handled or explicit block?
             # Let's rely on Manager state, but maybe log specific block here if desired.
             return False

        # 0. Budget Check (v21.0)
        # Note: We check allowance but don't increment yet (ledger counts executed events).
        if not self.budget_manager.check_allowance(self.device_trust_score):
             usage = self.budget_manager.get_usage(self.device_trust_score)
             print(f"[Scheduler] Blocked {cap.action_id}: Budget Exceeded. {usage.block_reason}")
             
             # Notify Recovery Manager (Budget Pressure)
             self.recovery_manager.notify_budget_exceeded()
             
             # Log Exceeded
             decision = AutonomyDecision(
                decision_id=str(uuid.uuid4()),
                decision_type=DecisionType.AUTONOMY_BUDGET_EXCEEDED,
                timestamp=time.time(),
                action_id=cap.action_id,
                reason=usage.block_reason,
                device_id=self.active_device_id
             )
             self.autonomy_ledger.append(decision)
             return False

        # 1. System Confidence
        conf = self.get_system_confidence()
        if conf.level == ConfidenceLevel.LOW:
            print(f"[Scheduler] Blocked {cap.action_id}: System Confidence is LOW.")
            return False
            
        # 2. Focus State (Block non-essential if Focused)
        if self.focus_state == "focus_session" and cap.risk_level != ActionRisk.LOW:
             print(f"[Scheduler] Blocked {cap.action_id}: User in Deep Work.")
             return False

        # 3. Risk Profile
        if cap.risk_level == ActionRisk.HIGH:
             print(f"[Scheduler] Blocked {cap.action_id}: High Risk actions disabled in v20.0.")
             return False
             
        if cap.risk_level == ActionRisk.MEDIUM and self.device_trust_score < 0.7:
             print(f"[Scheduler] Blocked {cap.action_id}: Trust Score too low for Medium Risk.")
             return False

        return True

    def record_action_outcome(self, action_id: str, status: ActionStatus):
        if status == ActionStatus.SUCCESS:
            print(f"[Scheduler] Action {action_id} Success. +Trust")
            self.update_device_trust(0.01) # Small increment
            
            # Log Budget Consumed
            decision = AutonomyDecision(
                decision_id=str(uuid.uuid4()),
                decision_type=DecisionType.AUTONOMY_BUDGET_CONSUMED,
                timestamp=time.time(),
                action_id=action_id,
                reason="Action Success consumes budget",
                device_id=self.active_device_id
             )
            self.autonomy_ledger.append(decision)

        elif status == ActionStatus.FAILED:
            print(f"[Scheduler] Action {action_id} Failed. -Trust")
            self.update_device_trust(-0.05) # Penalty
            self.recovery_manager.notify_failure() # v21.1
        # Re-calc confidence implicitly on next cycle or force?
        # Maybe force summary update if critical failure.
        
    def clear_presence(self):
        self.manual_presence_provider.clear()
        print("Presence override cleared.")
        self.save_user_context()

    def get_current_presence_state(self):
        return self.presence_resolver.resolve()

    def get_current_audience_tone(self):
        pres, _ = self.presence_resolver.resolve()
        aud = self.message_adapter.get_audience(pres)
        tone = self.message_adapter.get_tone(aud)
        return aud, tone

    def start_focus_session(self, duration_minutes: int):
        self.manual_focus_provider.start_focus(duration_minutes)
        self._focus_start_epoch = time.time()
        print(f"Focus Session Started: {duration_minutes}m")
        self.save_user_context()
        
    def stop_focus_session(self):
        self.manual_focus_provider.stop_focus()
        if hasattr(self, "_focus_start_epoch"):
             duration = int((time.time() - self._focus_start_epoch) / 60)
             self.pattern_detector.record_session(self._focus_start_epoch, duration)
             print(f"Focus Session Stopped. Recorded {duration}m for learning.")
             del self._focus_start_epoch
        else:
             print("Focus Session Stopped (No duration recorded).")
        self.save_user_context()
        self.save_user_context()
    
    def approve_focus_pattern(self, pattern_id: str):
        if self.pattern_consent.approve(pattern_id, self.user_interrupt_schedule):
            print(f"Focus Pattern {pattern_id} APPROVED.")
            self.save_user_context()
            
    def reject_focus_pattern(self, pattern_id: str):
        if self.pattern_consent.reject(pattern_id):
            print(f"Focus Pattern {pattern_id} REJECTED.")

    def get_current_focus_state(self):
        return self.focus_resolver.resolve()
        
    def get_active_proposals(self):
        return self.pattern_detector.get_proposals()

    def resolve_interrupt_request(self, request_id: str, action: str):
        """
        Called by API/UI to Approve or Reject a pending interrupt.
        """
        if request_id in self.pending_interrupts:
            req = self.pending_interrupts[request_id]
            if action == "APPROVE":
                req.status = InterruptRequestStatus.APPROVED
                self.interrupt_memory.record_outcome(req.reason, True)
                print(f"Interrupt {request_id} APPROVED.")
            elif action == "REJECT":
                req.status = InterruptRequestStatus.REJECTED
                self.interrupt_memory.record_outcome(req.reason, False)
                print(f"Interrupt {request_id} REJECTED.")
            
            # For v8.0 Verification, we persist pending longer or clear?
            # Let's keep in list but update status, UI filters active PENDING only.
            
    def get_preference_summary(self):
        # Helper to build summary for stream
        summary = {}
        all_hist = self.interrupt_memory.get_all_history()
        for reason, hist in all_hist.items():
            pref = self.consent_gate.inferer.infer(reason, hist)
            summary[str(reason)] = str(pref.bias.value)
        return summary
        
    def get_displayable_suggestions(self):
        """
        Returns list of suggestions allowed by Gating Rules.
        """
        # 1. Ask Policy what is technically Valid/Relevant
        # (Mock: currently just returns all active)
        candidates = self.proactive_engine.active_suggestions
        
        displayable = []
        
        # Helper for Ordering
        importance_score = {
            "low": 10,
            "medium": 20,
            "high": 30,
            "critical": 40
        }
        
        t_val = importance_score.get(self.preference_store.min_display_threshold.value, 20)
        
        # v16.1 Periodically run Adjustment Engine (every 60s)
        if time.time() - self.last_adjustment_check > 60:
            self.last_adjustment_check = time.time()
            self.current_agent_phase = AgentRole.GOVERNOR.value # Phase Switch
            # Scan recent ledger entries (last 100)
            entries = self.autonomy_ledger.get_entries()[-100:]
            self.adjustment_engine.scan_ledger_for_proposals(entries, context=GOVERNOR_CONTEXT)
            self.current_agent_phase = AgentRole.SYSTEM.value # Reset
        
        # v18.0 Export State Snapshot (Every tick, or throttled? Prompt says 'On tick end')
        # We'll throttle to avoid IO hammer
        if time.time() % 10 < 1: # Every ~10s
             self.latest_sync_state = self.state_exporter.export_sync_state()
        
        for s in candidates:
            # v15.1 Filtering Logic
            # Check domain/risk metadata
            meta = s.metadata
            domain = meta.get("domain", "unknown")
            # Risk enum requires conversion if stored as strings
            risk_str = meta.get("risk_level", "low")
            
            # Convert string to Enum for Resolver if needed, or Resolver handles strings?
            # My Resolver expects SignalRiskLevel enum.
            # I should convert back.
            try:
                from brain.external.external_signal_classification import SignalRiskLevel
                r_enum = SignalRiskLevel(risk_str)
            except:
                r_enum = SignalRiskLevel.LOW
                
            imp = self.alert_resolver.resolve(domain, r_enum)
            i_val = importance_score.get(imp.value, 20)
            
            # Determine visibility
            should_show = i_val >= t_val
            
            # Safety Hard Guard (CRITICAL + SAFETY domain bypasses filters) - Logic says "bypasses all filters"
            # Resolver already sets Critical Risk to Critical Importance.
            # So if threshold > Critical, it would be hidden?
            # Max Importance is Critical (40). So it always shows if Threshold is <= Critical.
            # This logic holds unless we mute Critical.
            
            if not should_show:
                if not s.is_filtered:
                     # State Change -> Valid Filter Event
                     s.is_filtered = True
                     s.filtered_reason = f"Preference Filter: {imp.value} < {self.preference_store.min_display_threshold.value}"
                     self._log_autonomy_decision(DecisionType.ALERT_FILTERED_BY_PREFERENCE, suggestion_id=s.suggestion_id, reason=s.filtered_reason, was_auto=False)
                     # v16.0 Reflection Hook
                     self.reflection_engine.process_event(ReflectionEvent(
                         event_type=ReflectionEventType.ALERT_FILTERED,
                         domain=domain,
                         item_id=s.suggestion_id
                     ), context=ANALYST_CONTEXT)
            else:
                 # It should show
                 if s.is_filtered:
                     # Was filtered, now shown (User changed pref?)
                     s.is_filtered = False
                     s.filtered_reason = None
                     self._log_autonomy_decision(DecisionType.ALERT_SHOWN_BY_PREFERENCE, suggestion_id=s.suggestion_id, reason=f"Preference Allowed: {imp.value}", was_auto=False)
                     # v16.0 Reflection Hook
                     self.reflection_engine.process_event(ReflectionEvent(
                         event_type=ReflectionEventType.ALERT_SHOWN,
                         domain=domain,
                         item_id=s.suggestion_id
                     ), context=ANALYST_CONTEXT)
            
            # Final output list construction (Existing logic + Filter check)
            # Only add if NOT filtered OR force visible?
            # "Filtering Layer... if computed_importance < USER_THRESHOLD -> hide"
            # But "Emergency Acknowledgment flow remains unchanged".
            # Force Visible suggestions (Emergencies) usually bypass?
            # Check visibility_level
            
            if s.visibility_level.value == "force_visible":
                displayable.append(s) # Always show Force Visible (Emergencies)
                continue
                
            if s.is_filtered:
                continue # Skip adding to displayable
                
            # Existing specific logic checks...
            # 2. Check Presence
            current_presence = self.get_current_presence_state()
            # ...
            
            displayable.append(s)
            
        return displayable

    def record_meaning_interaction(self, domain: str, interaction_type: InteractionType, source_id: str = "unknown"):
        """Records a user interaction to update meaning memory."""
        new_score = self.meaning_memory.record_interaction(domain, interaction_type)
        self._log_autonomy_decision(
            DecisionType.USER_MEANING_UPDATED, 
            suggestion_id=source_id, 
            reason=f"Type: {interaction_type.value}, Domain: {domain}, NewScore: {new_score:.2f}", 
            was_auto=False
        )

    def _should_create_suggestion(self, classification: ExternalSignal) -> bool:
        # Placeholder for actual logic
        return True # Default to true for now

    def resolve_proactive_suggestion(self, suggestion_id: str, action: str):
        if action == "DISMISS":
            # 1. Find Suggestion for ID logic
            sg = next((s for s in self.proactive_engine.active_suggestions if s.suggestion_id == suggestion_id), None)
            
            # v14.2 Record Meaning (Dismissal)
            if sg:
             # v15.1 Get Domain
             domain = sg.metadata.get("domain", "unknown")
             self.record_meaning_interaction(domain, InteractionType.DISMISS, source_id=suggestion_id)
             
             # v16.0 Reflection Hook
             self.reflection_engine.process_event(ReflectionEvent(
                 event_type=ReflectionEventType.ALERT_DISMISSED,
                 domain=domain,
                 item_id=suggestion_id
             ), context=ANALYST_CONTEXT)
        
            self.proactive_engine.dismiss(suggestion_id)
            print(f"Suggestion {suggestion_id} DISMISSED")
            if sg:
                self._log_autonomy_decision(DecisionType.EXTERNAL_SUGGESTION_BLOCKED, suggestion_id, sg.action_id, was_auto=False)
                if sg.action_id:
                    self.autonomy_policy.record_dismissal(sg.action_id)
                
        elif action == "ACCEPT":
            # 1. Find Suggestion
            sg = next((s for s in self.proactive_engine.active_suggestions if s.suggestion_id == suggestion_id), None)
            if not sg:
                 print(f"Suggestion {suggestion_id} not found.")
                 return
             
            # v16.0 Reflection Hook
            domain = sg.metadata.get("domain", "unknown")
            self.reflection_engine.process_event(ReflectionEvent(
                event_type=ReflectionEventType.USER_MANUAL_SEARCH,
                domain=domain,
                metadata={"query": query}
            ), context=ANALYST_CONTEXT)
             
            self.proactive_engine.accept(suggestion_id)
            print(f"Suggestion {suggestion_id} ACCEPTED")
            self._log_autonomy_decision(DecisionType.ACCEPTED, suggestion_id, sg.action_id, was_auto=False)
            
            # v11.2 Execute Action
            if sg.action_id:
                # RE-CHECK SAFETY GATES
                # Focus
                fs, _ = self.get_current_focus_state()
                if fs.value != "free":
                    print(f"Action Blocked: Focus is {fs.value}")
                    self._log_autonomy_decision(DecisionType.BLOCKED, suggestion_id, sg.action_id, reason=f"Focus: {fs.value}", was_auto=False)
                    return

                # Presence (Must be private for now for safety)
                ps, _ = self.get_current_presence_state()
                if ps.value == "with_others":
                    print(f"Action Blocked: Presence is Public")
                    self._log_autonomy_decision(DecisionType.BLOCKED, suggestion_id, sg.action_id, reason="Presence Public", was_auto=False)
                    return
                
                # Fetch and Execute
                act_def = self.action_registry.get_action(sg.action_id)
                if act_def:
                    print(f"Executing Action: {act_def.name}")
                    result = act_def.executor()
                    print(f"Action Result: {result}")
                    self.event_bus.emit(EventType.MISSION_COMPLETED, {"action": sg.action_id, "result": result})
                    # v11.3 Record Success
                    self.autonomy_policy.record_success(sg.action_id)
                else:
                    print(f"Action Definition {sg.action_id} not found.")
            
    def get_current_window_mode(self, reason=None) -> str:
        # Should now reflect Focus overrides!
        # If in Focus -> Silent.
        state, source = self.focus_resolver.resolve()
        if state in [FocusState.FOCUS_SESSION, FocusState.MEETING]:
            return "silent (focus)"
            
        # Mock reason for general status, or use None
        # Logic: If reason is None, we just check what window we are in regardless of reason
        # TimeGuard evaluate needs reason.
        # Let's peek at windows directly for status display
        import time
        now_struct = time.localtime()
        now_str = f"{now_struct.tm_hour:02d}:{now_struct.tm_min:02d}"
        for window in self.user_interrupt_schedule.windows:
            if window.contains_time(now_str):
                return str(window.mode.value)
        return "silent" # Default

    def _check_routine_conflicts(self, intent: 'Intent') -> Optional[float]:
         # Logic could be in Service, but needs Intent.
         # For MVP Headless, keep simple conflict check or move to Service.
         # Moving to minimal local check for now.
         now_seconds = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec
         for r in self.scheduler_service.get_protected_routines():
             if r.matches_time(now_seconds):
                 if intent.priority == IntentPriority.EMERGENCY: return None
                 end_seconds = r.time_of_day_seconds + r.duration_seconds
                 wait = end_seconds - now_seconds
                 if wait > 0: return time.time() + wait
         return None

    def schedule(self, mission_id: str, priority: MissionPriority, payload: Any = None, hints: List[OptimizationHint] = None, context: Optional[IntentContext] = None) -> str:
        hints = hints or []
        blocked_until = 0.0
        
        gate_decision = AttentionGateDecision.SILENT
        interrupt_reason = None
        interrupt_decision = "None"
        
        if context:
            self.last_intent_context = context
            gate_decision = self.attention_gate.evaluate(context)
            self.last_gate_decision = gate_decision
            interrupt_reason = context.interrupt_reason
            
            # Pre-calc qualifier logic if needed
            gate_qualified = False
            if gate_decision == AttentionGateDecision.CONDITIONAL:
                qual = self.interrupt_qualifier.qualify(context.interrupt_reason)
                gate_qualified = qual.qualified
                interrupt_decision = "APPROVED" if qual.qualified else "DEFERRED" 
                self.last_interrupt_decision = interrupt_decision
                self.last_interrupt_reason = str(interrupt_reason)
        
        # Optimization Hints
        for h in hints:
            if h.action == OptimizationAction.SCHEDULE_DELAY and h.parameter:
                blocked_until = time.time() + h.parameter

        new_intent = self._build_intent(mission_id, priority, payload)
        
        if new_intent:
            routine_defer = self._check_routine_conflicts(new_intent)
            if routine_defer:
                blocked_until = max(blocked_until, routine_defer)

        if new_intent and self._active_mission and blocked_until <= time.time():
             active_intent = self._build_intent(self._active_mission.mission_id, 
                                                MissionPriority(-self._active_mission.priority), 
                                                self._active_mission.payload)
             if active_intent:
                conflicts = self.conflict_detector.check_conflicts(new_intent, [active_intent])
                if conflicts:
                    report = conflicts[0]
                    resolution = self.conflict_policy.resolve(report)
                    
                    if resolution == self.Resolution.REJECT_NEW:
                        prefs = self.user_prefs.get(new_intent.user_id, SchedulingPreferences(user_id=new_intent.user_id))
                        decision = self.preference_resolver.resolve(report, prefs)
                        if decision.strategy == self.DeferralStrategy.DELAY:
                            blocked_until = decision.new_start_time
                        else:
                            return "REJECTED"
                    elif resolution == self.Resolution.ESCALATE:
                        blocked_until = time.time() + 999999
                    elif resolution == self.Resolution.OVERRIDE:
                        self._preempt_active()

        entry = QueuedMission(-priority.value, time.time(), mission_id, payload, blocked_until, hints)
        heapq.heappush(self._queue, entry)
        
        event_payload = {"mission_id": mission_id, "priority": priority.value}
        
        suppressed = False
        if context:
            event_payload["source_client_type"] = context.source_client_type
            event_payload["modality"] = context.modality
            event_payload["attention_state"] = context.attention_state
            event_payload["gate_decision"] = gate_decision
            event_payload["interrupt_reason"] = interrupt_reason
            event_payload["interrupt_decision"] = interrupt_decision
            
            # PRESENCE CHECK
            current_presence, _ = self.presence_resolver.resolve()
            
            if self.output_suppressor.should_suppress(gate_decision, EventType.MISSION_QUEUED, current_presence):
                suppressed = True
                # Check for Qualifier Override
                if gate_decision == AttentionGateDecision.CONDITIONAL and gate_qualified:
                     # If PUBLIC (WITH_OTHERS), we might still want to suppress even if Qualified?
                     # Plan says: "Suppress Personal/Interrupts... Allow Safety".
                     # Qualifier usually qualifies Priority/Safety.
                     # If Presence=Public, we might want to check if reason is Safety explicitly.
                     # For now, let's assume Qualifier=True implies strong necessity, but if it's "Optimized" -> Suppress.
                     # If it's DEADLINE -> Maybe allow?
                     # Simpler Logic: If Public -> Block unless SAFETY.
                     if current_presence == PresenceState.WITH_OTHERS and priority != MissionPriority.SAFETY:
                         suppressed = True
                     else:
                         suppressed = False # Override!
                
                # If STILL suppressed and was DEFERRED, check CONSENT GATE
        self.last_output_suppressed = suppressed
        self.event_bus.emit(EventType.MISSION_QUEUED, event_payload)
        
        return "SCHEDULED"

    def _build_intent(self, mid, pri, payload) -> Optional['Intent']:
        if isinstance(payload, MissionContract):
            ipri = IntentPriority.USER
            if pri == MissionPriority.CRITICAL: ipri = IntentPriority.EMERGENCY
            if pri == MissionPriority.BACKGROUND: ipri = IntentPriority.BACKGROUND
            
            return TemporalIntent(
                user_id=payload.created_by or "unknown",
                role=payload.execution_role or UserRole.OPERATOR,
                description=mid,
                priority=ipri,
                resources=payload.allowed_objects,
                mission_id=mid,
                flexibility=TimeFlexibility.FLEXIBLE
            )
        return None

    def get_day_snapshot(self):
        return self.scheduler_service.get_day_snapshot(self._queue)

    def get_week_snapshot(self):
        return self.scheduler_service.get_week_snapshot(self._queue)

    def get_load_snapshot(self):
        return self.scheduler_service.get_load_snapshot(self._queue)

    def check_reflection_triggers(self):
        wp = self.get_week_snapshot()
        ls = self.get_load_snapshot()
        prompt = self.memory_service.check_reflection_triggers(wp, ls)
        if prompt: self.active_reflection_prompt = prompt
        return prompt

    def simulate_scenario(self, scenario, context: Optional[IntentContext] = None):
        if context:
            self.last_intent_context = context
            # Sim is internal usually but track context
            self.last_gate_decision = self.attention_gate.evaluate(context)
            
        return self.simulation_service.simulate_scenario(scenario, self._queue)

    def create_proposal_from_scenario(self, scenario, context: Optional[IntentContext] = None):
        gate_decision = AttentionGateDecision.SILENT
        interrupt_reason = None
        interrupt_decision = "None"
        
        if context:
            self.last_intent_context = context
            gate_decision = self.attention_gate.evaluate(context)
            self.last_gate_decision = gate_decision
            interrupt_reason = context.interrupt_reason
            
            gate_qualified = False
            if gate_decision == AttentionGateDecision.CONDITIONAL:
                qual = self.interrupt_qualifier.qualify(context.interrupt_reason)
                gate_qualified = qual.qualified
                interrupt_decision = "APPROVED" if qual.qualified else "DEFERRED" 
                self.last_interrupt_decision = interrupt_decision
                self.last_interrupt_reason = str(interrupt_reason)
            
        proposal = self.simulation_service.create_proposal(scenario)
        
        event_payload = {"proposal_id": proposal.proposal_id}
        suppressed = False
        if context:
            event_payload["source_client_type"] = context.source_client_type
            event_payload["modality"] = context.modality
            event_payload["attention_state"] = context.attention_state
            event_payload["gate_decision"] = gate_decision
            
            if self.output_suppressor.should_suppress(gate_decision, EventType.COPLAN_PROPOSED):
                suppressed = True
                if gate_decision == AttentionGateDecision.CONDITIONAL and gate_qualified:
                     suppressed = False # Override!
                
                if suppressed and interrupt_decision == "DEFERRED":
                     current_focus, _ = self.focus_resolver.resolve()
                     if self.consent_gate.evaluate(interrupt_reason, self.user_interrupt_settings, self.user_interrupt_schedule, current_focus):
                         req = InterruptRequest.create(interrupt_reason)
                         self.pending_interrupts[req.request_id] = req
                         event_payload["interrupt_request_id"] = req.request_id
                
                event_payload["suppressed"] = suppressed
        
        self.last_output_suppressed = suppressed
        self.event_bus.emit(EventType.COPLAN_PROPOSED, event_payload)
        return proposal

    def apply_coplan_proposal(self, proposal):
        if not self.governance_service.check_quorum(proposal):
            return False
        
        result = self.simulation_service.apply_proposal(proposal, self)
        if result:
            self.event_bus.emit(EventType.COPLAN_QUORUM_MET, {"proposal_id": proposal.proposal_id})
        return result

    def undo_coplan_proposal(self, proposal):
        return self.simulation_service.undo_proposal(proposal, self)

    def register_coplan_vote(self, proposal, user_id, approved):
        self.governance_service.check_vote_authority(proposal, user_id, approved)
        self.event_bus.emit(EventType.COPLAN_VOTE_REGISTERED, {"proposal_id": proposal.proposal_id, "user_id": user_id, "approved": approved})


    # NOTE:
    # No feature flags, experimental branches, or conditional behavior
    # are allowed in tick() during stabilization.
    def _announce(self, text: str, force: bool = False):
        """H4: Trigger voice output via manager."""
        if hasattr(self, 'voice_manager'):
           self.voice_manager.speak(text, force=force)

    def tick(self, override_now: float = None) -> Optional[str]:
        # S6: Measure Tick Duration
        tick_start = time.monotonic()
        
        # H4: Track Recovery State
        prev_recovery = self.recovery_manager.state.level if self.recovery_manager.state else None
        
        # S5: Create Tick Context (Deterministic Scope)
        import uuid
        self._tick_context = TickContext(tick_id=str(uuid.uuid4()))
        
        self._current_tick_time = override_now if override_now is not None else time.time()
        self.event_bus.emit(EventType.SCHEDULER_TICK, {"time": self._current_tick_time})
        
        # Reset Cycle State
        self._current_phase = None
        self._cycle_signals = []
        self._cycle_active_suggestions = []
        self._cycle_decision = None # e.g. ("START", mission) or ("PREEMPT", None)
        self._cycle_auto_actions = []
        self._pending_ledger_entries = []
        
        self._run_observe_phase()
        self._run_analyze_phase()
        self._run_decide_phase()
        self._run_execute_phase()
        self._run_record_phase()
        
        self._current_phase = None
        
        # S6: Slow-Tick Detection & Backpressure
        elapsed_ms = (time.monotonic() - tick_start) * 1000
        self._last_tick_duration_ms = elapsed_ms
        
        # P3.2: Stall Detection (edge-triggered)
        if elapsed_ms >= SLOW_TICK_THRESHOLD_MS:
            # Slow tick detected
            self._consecutive_slow_ticks += 1
            self._consecutive_healthy_ticks = 0  # Reset healthy counter
            
            self._log_autonomy_decision(DecisionType.SLOW_TICK_DETECTED, reason=f"Duration: {elapsed_ms:.2f}ms", was_auto=False)
            
            # P3.2: Emit STALL ONCE after 3 consecutive slow ticks
            if self._consecutive_slow_ticks >= 3 and not self._stall_active:
                self._stall_active = True
                self._log_autonomy_decision(
                    DecisionType.SCHEDULER_STALL_DETECTED, 
                    reason=f"3 consecutive slow ticks (>{SLOW_TICK_THRESHOLD_MS}ms)", 
                    was_auto=False
                )
                self.event_bus.emit(EventType.SCHEDULER_STALL_DETECTED, {
                    "consecutive_slow_ticks": self._consecutive_slow_ticks,
                    "last_tick_ms": elapsed_ms
                })
                logger.warning(f"[P3.2] SCHEDULER_STALL_DETECTED: {self._consecutive_slow_ticks} slow ticks")
            
            # Backpressure Logic
            if elapsed_ms >= MAX_TICK_DURATION_MS:
                if not self._backpressure_active:
                    self._backpressure_active = True
                    self._log_autonomy_decision(DecisionType.BACKPRESSURE_ENABLED, reason=f"Tick exceeded {MAX_TICK_DURATION_MS}ms", was_auto=False)
        else:
            # Healthy tick
            self._consecutive_slow_ticks = 0  # Reset slow counter
            self._consecutive_healthy_ticks += 1
            
            # P3.2: Clear STALL ONCE after 2 consecutive healthy ticks
            if self._stall_active and self._consecutive_healthy_ticks >= 2:
                self._stall_active = False
                self._log_autonomy_decision(
                    DecisionType.SCHEDULER_STALL_CLEARED, 
                    reason=f"2 consecutive healthy ticks (<{SLOW_TICK_THRESHOLD_MS}ms)", 
                    was_auto=False
                )
                self.event_bus.emit(EventType.SCHEDULER_STALL_CLEARED, {
                    "consecutive_healthy_ticks": self._consecutive_healthy_ticks,
                    "last_tick_ms": elapsed_ms
                })
                logger.info(f"[P3.2] SCHEDULER_STALL_CLEARED: system recovered")
            
            if self._backpressure_active:
                self._backpressure_active = False
                self._log_autonomy_decision(DecisionType.BACKPRESSURE_CLEARED, reason=f"Tick recovered: {elapsed_ms:.2f}ms", was_auto=False)

        # P3.3: Resource Leak Detection (edge-triggered)
        queue_size = len(self._queue)
        pending_ledger = len(self._pending_ledger_entries)
        pending_actions = self._pending_actions_count
        
        # Check if any threshold exceeded
        leak_detected = (
            queue_size > MAX_QUEUE_SIZE or
            pending_ledger > MAX_PENDING_EVENTS or
            pending_actions > MAX_PENDING_ACTIONS
        )
        
        if leak_detected and not self._leak_suspected:
            # Edge trigger: entering leak state
            self._leak_suspected = True
            leak_reason = f"queue={queue_size}/{MAX_QUEUE_SIZE}, ledger={pending_ledger}/{MAX_PENDING_EVENTS}, actions={pending_actions}/{MAX_PENDING_ACTIONS}"
            self._log_autonomy_decision(
                DecisionType.RESOURCE_LEAK_SUSPECTED,
                reason=leak_reason,
                was_auto=False
            )
            self.event_bus.emit(EventType.RESOURCE_LEAK_SUSPECTED, {
                "queue_size": queue_size,
                "pending_ledger_entries": pending_ledger,
                "pending_actions": pending_actions
            })
            logger.warning(f"[P3.3] RESOURCE_LEAK_SUSPECTED: {leak_reason}")
        
        elif not leak_detected and self._leak_suspected:
            # Edge trigger: exiting leak state
            self._leak_suspected = False
            self._log_autonomy_decision(
                DecisionType.RESOURCE_LEAK_CLEARED,
                reason="All resource counters below thresholds",
                was_auto=False
            )
            self.event_bus.emit(EventType.RESOURCE_LEAK_CLEARED, {
                "queue_size": queue_size,
                "pending_ledger_entries": pending_ledger,
                "pending_actions": pending_actions
            })
            logger.info(f"[P3.3] RESOURCE_LEAK_CLEARED: system recovered")

        # P3.4: LLM Idle Memory Guard - check if model should be unloaded
        try:
            from brain.core.local_model_engine import local_engine
            import time
            if local_engine.is_loaded:
                idle_time = time.time() - local_engine._last_used_ts
                if idle_time > local_engine.IDLE_UNLOAD_SECONDS:
                    import asyncio
                    asyncio.create_task(local_engine.unload())
                    logger.info(f"[P3.4] Triggered LLM unload after {idle_time:.0f}s idle")
        except Exception as e:
            logger.debug(f"[P3.4] Idle check skipped: {e}")

        # S8: Populate Health Snapshot (Before clearing context)
        self._last_state_snapshot = {
            "last_tick_duration_ms": int(elapsed_ms),
            "backpressure_active": self._backpressure_active,
            "recovery_state": self.recovery_manager.state.level.name if self.recovery_manager.state else "NONE",
            "override_active": False, # Fixed later if method exists
            "startup_blocked": self._startup_blocked,
            "invariant_violations_last_tick": self._tick_context.invariant_violation_count
        }
        
        # Check override active properly
        if self.override_manager.get_active_token():
            self._last_state_snapshot["override_active"] = True

        # H4: Check Recovery Transition
        curr_recovery = self.recovery_manager.state.level if self.recovery_manager.state else None
        if prev_recovery and curr_recovery and prev_recovery != curr_recovery:
             # Import locally to compare if needed, or use string/value
             # Assuming RecoveryLevel is available or check names
             if curr_recovery.name == "HARD":
                 self._announce("Attention. System entering Hard Recovery.", force=True)
             elif prev_recovery.name == "HARD":
                 self._announce("System Stable. Recovery complete.", force=True)

        self._tick_context = None # Clear Scope
        return self._cycle_decision_outcome if hasattr(self, '_cycle_decision_outcome') else None

    # S7: Invariant Checking
    def _log_invariant_violation(self, code: str):
        self._tick_context.invariant_violation_count += 1
        self._pending_ledger_entries.append(AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.INVARIANT_VIOLATION,
            timestamp=time.time(),
            reason=f"Code: {code} | Phase: {self._current_phase.name if self._current_phase else 'None'} | Tick: {self._tick_context.tick_id}",
            device_id=self.active_device_resolver.resolve()[0] if self.active_device_resolver else "unknown"
        ))

    def _check_invariants(self):
        # 1. Never execute while startup is blocked
        # Note: We check execution_store state which might be loaded from disk or in-memory
        exec_state = self.execution_store.get_state()
        if self._startup_blocked and exec_state.action_phase == ActionPhase.EXECUTING:
            self._log_invariant_violation("EXECUTING_WHILE_STARTUP_BLOCKED")

        # 2. Backpressure forbids autonomous actions
        if self._backpressure_active and self._cycle_auto_actions:
            self._log_invariant_violation("AUTO_ACTIONS_DURING_BACKPRESSURE")

        # 3. HARD recovery forbids autonomy without override
        # RecoveryLevel.HARD check
        if (
            self.recovery_manager.state.level == RecoveryLevel.HARD
            and not self.override_manager.get_active_token()
            and self._cycle_auto_actions
        ):
            self._log_invariant_violation("AUTO_ACTIONS_DURING_HARD_RECOVERY")

        # FAIL FAST: If any invariant violation was logged this tick, we must Halt.
        # We need to scan pending ledger entries for violation type efficiently.
        # Since this method is called after decisions/before execution, we only care about
        # violations generated JUST NOW or earlier in this tick.
        
        # Check pending violations in context
        # Or scan _pending_ledger_entries for INVARIANT_VIOLATION
        for entry in self._pending_ledger_entries:
            if entry.decision_type == DecisionType.INVARIANT_VIOLATION:
                 raise RuntimeError("Invariant violation detected — execution halted")

    # PHASE GUARANTEE:
    # This method must not call later phases.
    # No cross-phase side effects allowed.
    def _run_observe_phase(self):
        """Collect signals, device state, external inputs"""
        self._enter_phase(BrainPhase.OBSERVE)
        
        # v11.0 Ambient Observer
        self.ambient_observer.tick()
        
        # H6: Context Signals (App/Calendar)
        # We poll and log only on change to avoid noise
        try:
            app_sig = self.app_provider.get_context()
            if app_sig and app_sig.data != self._last_app_context_data:
                 self._last_app_context_data = app_sig.data
                 self._log_autonomy_decision(DecisionType.CONTEXT_SIGNAL_RECEIVED, reason=f"App: {app_sig.data}", was_auto=False)
                 
            cal_sig = self.calendar_provider.check_status()
            if cal_sig and cal_sig.data != self._last_cal_context_data:
                 self._last_cal_context_data = cal_sig.data
                 self._log_autonomy_decision(DecisionType.CONTEXT_SIGNAL_RECEIVED, reason=f"Calendar: {cal_sig.data.get('status')}", was_auto=False)
        except Exception as e:
            print(f"[CONTEXT] Provider Error: {e}")

        # v12.0 External Observer
        # S6: Check Backpressure
        if self._backpressure_active:
             # Skip expensive external signal processing
             self._cycle_signals = []
        else:
             self._cycle_signals = self.external_observer.tick()

    # PHASE GUARANTEE:
    # This method must not call later phases.
    # No cross-phase side effects allowed.
    def _run_analyze_phase(self):
        """Reflection, summaries, confidence updates"""
        self._enter_phase(BrainPhase.ANALYZE)
        
        # v12.3 Check Escalations
        escalated = self.emergency_manager.check_escalation()
        for e in escalated:
            print(f"[EMERGENCY] Escalated to Level {e.escalation_level} (ID: {e.emergency_id})")
            self._log_autonomy_decision(DecisionType.EMERGENCY_ESCALATED, suggestion_id=e.suggestion_id, reason=f"Level {e.escalation_level}", was_auto=False)
            
        # v11.1 Proactive Insights
        # Feed insights to engine
        # S6: Check Backpressure & H10: Annoyance Budget
        if self._backpressure_active:
             self._cycle_proactive_suggestions = []
        elif not self.trust_gate.check_budget():
             # H10: Budget Exceeded
             # Log once per suppression? No, just silence or log decision.
             # We'll log simplified decision
             self._log_autonomy_decision(DecisionType.ATTENTION_SUPPRESSED, reason="Annoyance Budget Exceeded", was_auto=True)
             self._cycle_proactive_suggestions = []
        else:
             suggestions = self.proactive_engine.process_insights(self.ambient_observer.insights)
             if suggestions:
                 self.trust_gate.consume_budget()
             self._cycle_proactive_suggestions = suggestions

    # PHASE GUARANTEE:
    # This method must not call later phases.
    # No cross-phase side effects allowed.
    def _run_decide_phase(self):
        """Decisions, suggestions, action selection"""
        self._enter_phase(BrainPhase.DECIDE)
        self._cycle_decision_outcome = None
        
        # 1. Process External Signals (Decision Logic)
        for sig in self._cycle_signals:
            print(f"[EXTERNAL] Signal Classified: [{sig.domain.value.upper()}/{sig.risk_level.value.upper()}] {sig.title}")
            reason_txt = f"{sig.source}: {sig.title} (Risk: {sig.risk_level.value})"
            self._log_autonomy_decision(DecisionType.EXTERNAL_SIGNAL_CLASSIFIED, reason=reason_txt, was_auto=False)
            
            # v12.1 Bridge to Suggestions
            trust, _ = self.get_confidence_info()
            fs, _ = self.get_current_focus_state()
            ps, _ = self.get_current_presence_state()
            style = self.user_interrupt_settings.style
            
            # v12.0 Check Emergency Visibility First
            vis, why = self.emergency_policy.check_visibility(sig)
            is_emergency = (vis == "FORCE_VISIBLE")
            
            if is_emergency:
                allowed = True
                block_reason = ""
            else:
                allowed, block_reason = self.external_policy.should_allow_suggestion(
                    sig, trust, fs.value != "free", ps.value == "with_others", style
                )
            
            if allowed:
                suggestion = self.external_adapter.to_suggestion(sig)
                
                # Apply Visibility
                if is_emergency:
                    suggestion.visibility_level = VisibilityLevel.FORCE_VISIBLE
                    suggestion.visibility_explanation = why
                    self._log_autonomy_decision(DecisionType.EMERGENCY_VISIBILITY_GRANTED, suggestion_id=suggestion.suggestion_id, reason=why, was_auto=False)
                    
                    # v12.3 Create Acknowledgment Tracker
                    ack = self.emergency_manager.create_emergency(sig.signal_id, suggestion.suggestion_id)
                    self._log_autonomy_decision(DecisionType.EMERGENCY_ACK_CREATED, suggestion_id=suggestion.suggestion_id, reason=f"Emergency ID: {ack.emergency_id}", was_auto=False)
                    
                    # v13.0 Contextual Search (Read-Only)
                    search_res = self.contextual_search.perform_search(query=sig.title + " mitigation", signal_id=sig.signal_id)
                    self._log_autonomy_decision(DecisionType.CONTEXTUAL_SEARCH_PERFORMED, suggestion_id=suggestion.suggestion_id, reason=f"Conf: {search_res.confidence_score}", was_auto=False)
                    
                    # v13.1 Contextual Narrator
                    narration = self.contextual_narrator.narrate(search_res)
                    
                    # Store
                    meta = {
                        "title": sig.title, 
                        "domain": sig.domain.value, 
                        "risk_level": sig.risk_level.value,
                        "signal_id": sig.signal_id
                    }
                    self.contextual_memory.add(narration, meta)
                    self._log_autonomy_decision(DecisionType.CONTEXTUAL_MEMORY_RECORDED, suggestion_id=suggestion.suggestion_id, reason=f"Stored: {sig.title}", was_auto=False)
                    
                    # Analyze
                    insight = self.pattern_analyzer.analyze_pattern(sig.title)
                    narration.historical_occurrences_7d = insight.count
                    narration.trend_label = insight.trend
                    
                    # Log Pattern
                    self._log_autonomy_decision(DecisionType.CONTEXTUAL_PATTERN_DETECTED, suggestion_id=suggestion.suggestion_id, reason=f"Trend: {insight.trend} Conf: {insight.confidence}", was_auto=False)
                    
                    # v14.1 Pattern Explanation
                    explanation = self.pattern_narrator.explain(insight, sig.title)
                    self._log_autonomy_decision(DecisionType.CONTEXTUAL_PATTERN_EXPLAINED, suggestion_id=suggestion.suggestion_id, reason=f"Explained: {explanation.trend_label}", was_auto=False)
                
                self.proactive_engine.active_suggestions.append(suggestion)
                print(f"[EXTERNAL] Suggestion Created: {suggestion.message} (Vis: {suggestion.visibility_level.value})")
                self._log_autonomy_decision(DecisionType.EXTERNAL_SUGGESTION_CREATED, suggestion_id=suggestion.suggestion_id, reason=f"From {sig.signal_id}", was_auto=False)
            else:
                self._log_autonomy_decision(DecisionType.EXTERNAL_SUGGESTION_BLOCKED, reason=f"{block_reason} (Signal: {sig.signal_id})", was_auto=False)
        
        # 2. Process Proactive Suggestions (Auto-Execution Logic)
        for sg in self._cycle_proactive_suggestions:
            # Log SUGGESTED
            self._log_autonomy_decision(DecisionType.SUGGESTED, sg.suggestion_id, sg.action_id, sg.message, was_auto=False)
            
            if sg.action_id:
                # Gather Context
                trust_score, _ = self.get_confidence_info()
                fs, _ = self.get_current_focus_state()
                ps, _ = self.get_current_presence_state()
                style = self.user_interrupt_settings.style
                act_def = self.action_registry.get_action(sg.action_id)
                
                if act_def:
                    allowed, reason = self.autonomy_policy.may_auto_execute(
                        sg.action_id, act_def, trust_score, style, 
                        fs.value != "free", ps.value == "with_others"
                    )
                    
                    if allowed:
                        print(f"[AUTONOMY] Scheduling Auto-Execution for {sg.action_id} (Reason: {reason})")
                        # DEFER EXECUTION to Execute Phase
                        self._cycle_auto_actions.append((sg, act_def, reason))
                        
        if self._cycle_proactive_suggestions:
             print(f"[PROACTIVE] Processed {len(self._cycle_proactive_suggestions)} new suggestions.")

        # 3. Queue Logic
        if not self._queue: return
        
        top_mission = self._queue[0]
        if top_mission.blocked_until > time.time(): return
        
        if not self._active_mission:
            # Decision: START NEW
            self._cycle_decision = ("START", heapq.heappop(self._queue))
            self._cycle_decision_outcome = "START_NEW"
            return
            
        if top_mission.priority < self._active_mission.priority:
            # Check Concurrency
            avoid = any(h.action == OptimizationAction.AVOID_CONCURRENCY for h in top_mission.hints)
            if avoid: return
            
            # Decision: PREEMPT
            self._cycle_decision = ("PREEMPT", None)
            self._cycle_decision_outcome = "PREEMPT"
            return

        # S7: Invariant Check (Post-Decision)
        self._check_invariants()
            
    def _check_startup_recovery(self):
        # S4: Check for Crash Interruption
        state = self.execution_store.get_state()
        if state.action_phase == ActionPhase.INTERRUPTED:
            self._startup_blocked = True
            logger.critical(f"STARTUP BLOCKED: Previous execution interrupted at {state.interrupted_at}. User intervention required.")

    def clear_startup_block(self):
        """
        Manually clears the startup block.
        Only called by explicit user action (Retry/Abort).
        """
        if self._startup_blocked:
            logger.info("Manual intervention received. Clearing startup block.")
            self._startup_blocked = False

    # PHASE GUARANTEE:
    # This method must not call later phases.
    # No cross-phase side effects allowed.
    def _run_execute_phase(self):
        """Sandboxed execution only"""
        self._enter_phase(BrainPhase.EXECUTE)
        
        # S7: Invariant Check (Pre-Execution)
        self._check_invariants()
        
        # S4: Execution Guard
        if self._startup_blocked:
             raise RuntimeError(
                "Execution blocked: previous action was interrupted. "
                "User must explicitly Retry or Abort."
            )
        
        # 1. Mission Lifecycle Execution
        if self._cycle_decision:
            action, payload = self._cycle_decision
            if action == "START":
                self._start_mission(payload)
            elif action == "PREEMPT":
                self._preempt_active()
        
        # 2. Proactive Auto-Execution
        for item in self._cycle_auto_actions:
            sg, act_def, reason = item
            try:
                # INVARIANT: Execution allowed only in EXECUTE phase
                self._assert_phase([BrainPhase.EXECUTE])
                
                # S5: Actuation Idempotency Guard
                action_key = f"{self._tick_context.tick_id}:{sg.action_id}"
                if action_key in self._tick_context.executed_actions:
                     print(f"[IDEMPOTENCY] Skipped duplicate action {sg.action_id} in tick {self._tick_context.tick_id}")
                     continue
                self._tick_context.executed_actions.add(action_key)
                
                result = act_def.executor()
                sg.status = SuggestionStatus.AUTO_EXECUTED
                self.autonomy_policy.record_success(sg.action_id)
                
                # Log execution success (Buffered)
                self._log_autonomy_decision(DecisionType.AUTO_EXECUTED, sg.suggestion_id, sg.action_id, reason, was_auto=True)
                self.event_bus.emit(EventType.MISSION_COMPLETED, {"action": sg.action_id, "result": result, "mode": "AUTO"})
            except Exception as e:
                print(f"[AUTONOMY] Execution Failed: {e}")
                self.autonomy_policy.disable_autonomy(f"Execution Error: {e}")

    # PHASE GUARANTEE:
    # This method must not call later phases.
    # No cross-phase side effects allowed.
    def _run_record_phase(self):
        """Ledger, persistence, memory writes"""
        self._enter_phase(BrainPhase.RECORD)
        
        # 1. Flush Ledger
        if self._pending_ledger_entries:
            self._assert_phase([BrainPhase.RECORD])
            for d in self._pending_ledger_entries:
                # S5: Ledger Idempotency Guard
                entry_key = f"{self._tick_context.tick_id}:{d.decision_type.value}:{d.decision_id}"
                if entry_key in self._tick_context.ledger_entries:
                    continue
                
                self._tick_context.ledger_entries.add(entry_key)
                self.autonomy_ledger.append(d)
                
            self._pending_ledger_entries.clear()
            
        # 2. Persist User Context if needed (Optional hook, usually strictly on events, but safe here)
        # self.save_user_context() # Not strictly required every tick, expensive.
        pass


    def _start_mission(self, mission):
        self._active_mission = mission
        self.event_bus.emit(EventType.MISSION_STARTED, {"mission_id": mission.mission_id})
        logger.info(f"Starting: {mission.mission_id}")
        
    def _preempt_active(self):
        if self._active_mission:
            heapq.heappush(self._queue, self._active_mission)
            self.event_bus.emit(EventType.MISSION_PREEMPTED, {"mission_id": self._active_mission.mission_id})
            self._active_mission = None
            
    def complete_active(self):
        if self._active_mission:
             self.event_bus.emit(EventType.MISSION_COMPLETED, {"mission_id": self._active_mission.mission_id})
             self._active_mission = None
             
    # v11.4 Autonomy Ledger Helper
    def _log_autonomy_decision(self, type: DecisionType, suggestion_id: str = None, action_id: str = None, reason: str = None, was_auto: bool = False):
        try:
            import time
            import uuid
            
            trust, _ = self.get_confidence_info()
            fs, _ = self.get_current_focus_state()
            ps, _ = self.get_current_presence_state()
            style = self.user_interrupt_settings.style
            
            # Simple device resolution (assume active or last active)
            dev_id = "unknown"
            if self.active_device_resolver:
                 resolved_id, _ = self.active_device_resolver.resolve()
                 if resolved_id:
                     dev_id = resolved_id
            
            decision = AutonomyDecision(
                decision_id=str(uuid.uuid4()),
                decision_type=type,
                timestamp=time.time(),
                suggestion_id=suggestion_id,
                action_id=action_id,
                reason=reason or "",
                trust_score=trust,
                focus_state=fs.value,
                presence_state=ps.value,
                interrupt_style=style.value,
                device_id=dev_id,
                was_auto=was_auto
            )
            # S3: Buffer decisions for RECORD phase
            self._pending_ledger_entries.append(decision)
            
        except Exception as e:
            print(f"[LEDGER] Error logging decision: {e}")


mission_scheduler = MissionScheduler()
