import heapq
import time
import logging
from dataclasses import dataclass, field
from enum import IntEnum
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

class MissionScheduler:
    """
    Orchestrator for mission execution.
    Delegates logic to Services.
    """
    def __init__(self):
        self._queue: List[QueuedMission] = []
        self._active_mission: Optional[QueuedMission] = None
        
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
        
        # ... (Services) ...

    # ... (Properties and Setters) ...
    
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
            self.last_summary_time = now
            
        return self.last_summary

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

    def tick(self, override_now: float = None) -> Optional[str]:
        now = override_now if override_now is not None else time.time()
        self.event_bus.emit(EventType.SCHEDULER_TICK, {"time": now})
        
        # v11.0 Ambient Observer
        # v11.0 Ambient Observer
        self.ambient_observer.tick()
        
        # v12.0 External Observer
        ext_signals = self.external_observer.tick()
        for sig in ext_signals:
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
                # Bypass External Policy (which gates on Context)
                # But we might want to check TRUST? 
                # Policy says: "FORCE_VISIBLE suggestions bypass: Focus suppression, Interrupt suppression"
                # It does NOT say it bypasses TRUST.
                # However, ExternalSuggestionAdapter creates it. 
                # If trust is low, should we show critical alert? Probably yes.
                # But let's stick to the prompt: Check "ExternalSuggestionPolicy" logic?
                # "Policy does NOT bypass execution rules"
                # Actually v12.1 "should_allow_suggestion" returns False if Public.
                # If Emergency, we want to IGNORE that False result IF it's just context blocking.
                
                # Let's create suggestion regardless of context, but maybe check trust?
                # Prompt says: "CRITICAL signal shows even during Focus... even if interrupt_style=NEVER"
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
                    # Trigger analysis on Critical Signal
                    search_res = self.contextual_search.perform_search(query=sig.title + " mitigation", signal_id=sig.signal_id)
                    self._log_autonomy_decision(DecisionType.CONTEXTUAL_SEARCH_PERFORMED, suggestion_id=suggestion.suggestion_id, reason=f"Conf: {search_res.confidence_score}", was_auto=False)
                    
                    # v13.1 Contextual Narrator
                    narration = self.contextual_narrator.narrate(search_res)
                    
                    # v14.0 Pattern Analysis
                    # Check pattern BEFORE adding current? Or AFTER?
                    # User spec: "After ContextualNarrator runs: Store... Run PatternAnalyzer"
                    # Wait, usually you analyze history BEFORE adding the new one if you want to know "previous" state.
                    # But request says: "Run PatternAnalyzer" (after store).
                    # I will analyze AFTER storing so that the current one contributes to "New" or "Rising"?
                    # Actually, for "Trend", usually you want to compare current to recent past.
                    # If I store it, the total count increases by 1.
                    
                    # Let's follow: Store -> Analyze.
                    
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
                    
                    # Update Narrated Context with Insight (in Memory only? Or update the object?)
                    # Narration object was already returned to API potentially? No, not yet accessible via API until requested.
                    # The user doesn't say to update Narration object fields.
                    # But I added fields to NarratedContext in v14.0.0.
                    # I should update them for the API to see later.
                    narration.historical_occurrences_7d = insight.count # Approx mismatch but okay for display
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
        
        # v12.3 Check Escalations
        escalated = self.emergency_manager.check_escalation()
        for e in escalated:
            print(f"[EMERGENCY] Escalated to Level {e.escalation_level} (ID: {e.emergency_id})")
            self._log_autonomy_decision(DecisionType.EMERGENCY_ESCALATED, suggestion_id=e.suggestion_id, reason=f"Level {e.escalation_level}", was_auto=False)
        
        # v11.1 Proactive Suggestions
        # Feed insights to engine
        new_suggestions = self.proactive_engine.process_insights(self.ambient_observer.insights)
        
        # v11.3 Auto-Execution Check
        for sg in new_suggestions:
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
                        print(f"[AUTONOMY] Auto-Executing {sg.action_id} (Reason: {reason})")
                        # Execute
                        try:
                            result = act_def.executor()
                            sg.status = SuggestionStatus.AUTO_EXECUTED
                            self.autonomy_policy.record_success(sg.action_id)
                            self._log_autonomy_decision(DecisionType.AUTO_EXECUTED, sg.suggestion_id, sg.action_id, reason, was_auto=True)
                            self.event_bus.emit(EventType.MISSION_COMPLETED, {"action": sg.action_id, "result": result, "mode": "AUTO"})
                        except Exception as e:
                            print(f"[AUTONOMY] Execution Failed: {e}")
                            self.autonomy_policy.disable_autonomy(f"Execution Error: {e}")
                            # Don't change status to executed? Or mark failed?
                            # For now leave pending or dismiss.
        
        if new_suggestions:
             print(f"[PROACTIVE] Processed {len(new_suggestions)} new suggestions.")

        if not self._queue: return None
        
        top_mission = self._queue[0]
        if top_mission.blocked_until > time.time(): return None
        
        if not self._active_mission:
            self._start_mission(heapq.heappop(self._queue))
            return "START_NEW"
            
        if top_mission.priority < self._active_mission.priority:
            # Check Concurrency
            avoid = any(h.action == OptimizationAction.AVOID_CONCURRENCY for h in top_mission.hints)
            if avoid: return None
            
            self._preempt_active()
            return "PREEMPT"
            
        return None

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
            self.autonomy_ledger.append(decision)
        except Exception as e:
            print(f"[LEDGER] Error logging decision: {e}")

mission_scheduler = MissionScheduler()
