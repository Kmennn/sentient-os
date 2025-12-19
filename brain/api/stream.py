from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict, Optional
from brain.events.event_bus import event_bus
from brain.events.event_types import EventType
from brain.state.state_snapshot import SystemState, MissionModel, QueueItem
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.memory.meaning_memory import InteractionType
import asyncio
import logging

from brain.presence.presence_registry import presence_registry
from brain.presence.client import ClientType

from brain.api.autonomy_history import router as autonomy_router
from brain.api.external_signals import router as external_signals_router
from brain.api.emergency import router as emergency_router
from brain.api.contextual import router as contextual_router
from brain.api.memory import router as memory_router
from brain.api.preferences import router as preferences_router
from brain.api.reflection import router as reflection_router
from brain.api.adjustments import router as adjustments_router
from brain.api.sync import router as sync_router

logger = logging.getLogger("API")

app = FastAPI()
app.include_router(autonomy_router)
app.include_router(external_signals_router)
app.include_router(emergency_router)
app.include_router(contextual_router)
app.include_router(memory_router)
app.include_router(preferences_router)
app.include_router(reflection_router)
app.include_router(adjustments_router)
app.include_router(sync_router)
app.include_router(sync_router)
app.include_router(timeline_router)
app.include_router(confidence_router)
app.include_router(actions_router)
app.include_router(budget_router)
app.include_router(memory_router)
app.include_router(preferences_router)

def get_current_state() -> SystemState:
    # Build Snapshot from Scheduler
    active = None
    if mission_scheduler._active_mission:
        active = MissionModel(
            mission_id=mission_scheduler._active_mission.mission_id,
            priority=-mission_scheduler._active_mission.priority, # Remember Priority was negated
            started_at=mission_scheduler._active_mission.timestamp
        )

    queue = []
    for item in mission_scheduler._queue:
        queue.append(QueueItem(
            mission_id=item.mission_id,
            priority=-item.priority,
            blocked_until=item.blocked_until
        ))
        
    import time
    last_intent_source = None
    last_intent_modality = None
    last_intent_attention = None
    last_gate_decision = None
    last_suppressed = False
    if mission_scheduler.last_intent_context:
        curr_ctx = mission_scheduler.last_intent_context
        last_intent_source = curr_ctx.source_client_type
        last_intent_modality = curr_ctx.modality
        last_intent_attention = curr_ctx.attention_state
    
    if mission_scheduler.last_gate_decision:
        last_gate_decision = mission_scheduler.last_gate_decision
        
    last_suppressed = mission_scheduler.last_output_suppressed
    last_reason = mission_scheduler.last_interrupt_reason
    last_decision = mission_scheduler.last_interrupt_decision
    
    pending_reqs = []
    for req in mission_scheduler.pending_interrupts.values():
        if req.status == "pending": # Use string if StrEnum or .value
             pending_reqs.append({
                 "request_id": req.request_id,
                 "reason": req.reason,
                 "message": req.message,
                 "created_at": req.created_at
             })
             
    pref_summary = mission_scheduler.get_preference_summary()
    style = mission_scheduler.user_interrupt_settings.style
    window_mode = mission_scheduler.get_current_window_mode()
    focus_st, focus_src = mission_scheduler.get_current_focus_state()
    
    proposals = []
    for p in mission_scheduler.get_active_proposals():
        proposals.append({
            "pattern_id": p.pattern_id,
            "start_time": p.start_time,
            "end_time": p.end_time,
            "confidence": p.confidence
        })
        
    pres_st, pres_src = mission_scheduler.get_current_presence_state()
    aud, tone = mission_scheduler.get_current_audience_tone()
    dev_id, dev_conf = mission_scheduler.get_active_device_info()
    ctx_status = mission_scheduler.context_window_manager.get_status()
    conf_score, conf_lvl = mission_scheduler.get_confidence_info()

    # Build Device List
    dev_list = []
    # Note: get_active_devices only returns active. Users might want to see recently active too?
    # For now, just active is fine, or we could expose all from registry.
    # Let's access registry directly for fullness if needed, but registry.get_active_devices() is safer.
    active_devs = mission_scheduler.device_registry.get_active_devices()
    for d in active_devs:
        score = mission_scheduler.device_confidence_manager.get_score(d.device_id)
        dev_list.append({
            "id": d.device_id,
            "type": d.device_type.value,
            "trust": round(score, 2),
            "active": (d.device_id == dev_id)
        })

    return SystemState(
        tick_time=time.time(),
        active_mission=active,
        queue=queue,
        connected_clients=presence_registry.client_count,
        clients_summary=presence_registry.get_summary(),
        last_intent_source_type=last_intent_source,
        last_intent_modality=last_intent_modality,
        last_intent_attention_state=last_intent_attention,
        last_attention_gate_decision=last_gate_decision,
        last_output_suppressed=last_suppressed,
        last_interrupt_reason=last_reason,
        last_interrupt_decision=last_decision,
        pending_interrupt_requests=pending_reqs,
        interrupt_preference_summary=pref_summary,
        interrupt_style=str(style.value),
        current_window_mode=window_mode,
        focus_state=str(focus_st.value),
        focus_source=focus_src,
        focus_pattern_proposals=proposals,
        presence_state=str(pres_st.value),
        presence_source=pres_src,
        audience_mode=str(aud.value),
        tone_profile=str(tone.value),
        last_output_channel=mission_scheduler.last_output_channel,
        last_output_targets=mission_scheduler.last_output_targets,
        connected_devices=len(mission_scheduler.device_registry.get_active_devices()),
        active_device=str(dev_id) if dev_id else "none",
        active_device_confidence=round(dev_conf, 2),
        last_handoff= f"{mission_scheduler.last_handoff.from_device_id}->{mission_scheduler.last_handoff.to_device_id}" if mission_scheduler.last_handoff else "none",
        has_context_window=ctx_status["active"],
        context_source_device=ctx_status["source"] or "none",
        context_expires_in_ms=ctx_status["expires_in"] * 1000,
        confidence_level=conf_lvl,
        device_trust_score=round(conf_score, 2),
        device_list=dev_list,
        pending_proactive_suggestions=[s.to_dict() for s in mission_scheduler.get_displayable_suggestions()],
        # v11.3
        autonomy_active=mission_scheduler.autonomy_policy.enabled,
        # v12.2
        last_emergency_visible=any(s.visibility_level.value == "force_visible" for s in mission_scheduler.get_displayable_suggestions()),
        last_emergency_reason=next((s.visibility_explanation for s in mission_scheduler.get_displayable_suggestions() if s.visibility_level.value == "force_visible"), ""),
        # v12.3
        pending_emergency_count=len(mission_scheduler.emergency_manager.get_pending()),
        highest_escalation_level=mission_scheduler.emergency_manager.get_highest_level(),
        # v13.1
        last_contextual_narration_available=len(mission_scheduler.contextual_narrator._narrations) > 0,
        # v14.0
        contextual_history_count=len(mission_scheduler.contextual_memory._history),
        last_pattern_detected=len(mission_scheduler.contextual_memory._history) > 3, # Proxy for "enough data"
        # v14.1
        last_pattern_explanation_available=len(mission_scheduler.pattern_narrator._explanations) > 0,
        # v14.2
        meaning_memory_available=True,
        # v15.0
        explicit_preferences_available=True,
        # v15.1
        last_alert_filtered=any(s.is_filtered for s in mission_scheduler.proactive_engine.active_suggestions),
        # v16.0
        last_reflection_signal=mission_scheduler.reflection_engine.last_reflection_signal,
        reflection_confidence=mission_scheduler.reflection_engine.reflection_confidence,
        # v16.1
        pending_adjustments_count=len([p for p in mission_scheduler.adjustment_engine.active_proposals.values() if p.status.value == "pending"]),
        # v17.0
        last_active_agent=mission_scheduler.current_agent_phase, # Simplified mapping
        agent_phase=mission_scheduler.current_agent_phase
    )

@app.post("/interrupts/{request_id}/respond")
async def respond_to_interrupt(request_id: str, action: str):
    # action: APPROVE or REJECT
    mission_scheduler.resolve_interrupt_request(request_id, action)
    return {"status": "processed", "action": action}

@app.post("/settings/interrupt-style")
async def set_interrupt_style(style: str):
    # style: never_interrupt, always_ask, ask_for_important
    mission_scheduler.set_interrupt_style(style)
    return {"status": "updated", "style": style}

@app.post("/focus/start")
async def start_focus(duration_minutes: int = 25):
    mission_scheduler.start_focus_session(duration_minutes)
    return {"status": "started", "duration": duration_minutes}

@app.post("/focus/stop")
async def stop_focus():
    mission_scheduler.stop_focus_session()
    return {"status": "stopped"}

@app.post("/focus/pattern/{pattern_id}/approve")
async def approve_pattern(pattern_id: str):
    mission_scheduler.approve_focus_pattern(pattern_id)
    return {"status": "approved", "pattern_id": pattern_id}

@app.post("/focus/pattern/{pattern_id}/reject")
async def reject_pattern(pattern_id: str):
    mission_scheduler.reject_focus_pattern(pattern_id)
    return {"status": "rejected", "pattern_id": pattern_id}

@app.post("/presence/public")
async def set_presence_public():
    mission_scheduler.set_presence_public()
    return {"status": "public"}

@app.post("/presence/private")
async def set_presence_private():
    mission_scheduler.set_presence_private()
    return {"status": "private"}

@app.post("/presence/clear")
async def clear_presence():
    mission_scheduler.clear_presence()
    return {"status": "cleared"}

from pydantic import BaseModel, Field

class DeviceHeartbeat(BaseModel):
    device_id: str
    device_type: str = "desktop"
    capabilities: List[str] = ["TOAST", "PANEL"]

@app.post("/devices/heartbeat")
async def device_heartbeat(hb: DeviceHeartbeat):
    mission_scheduler.register_device(hb.device_id, hb.device_type, hb.capabilities)
    return {"status": "registered"}

class DeviceInteraction(BaseModel):
    device_id: str
    interaction_type: str = "input" # focus, input, view, ping

@app.post("/devices/interaction")
async def device_interaction(action: DeviceInteraction):
    mission_scheduler.report_interaction(action.device_id, action.interaction_type)
    return {"status": "recorded"}

@app.post("/suggestions/{suggestion_id}/resolve")
async def resolve_suggestion(suggestion_id: str, action: str):
    # action: ACCEPT or DISMISS
    mission_scheduler.resolve_proactive_suggestion(suggestion_id, action.upper())
    return {"status": "resolved", "action": action}

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket, client_type: str = "UI"):
    await websocket.accept()
    
    # Register Presence
    # (In real prod, get real IP from request.client.host)
    ctype = ClientType.UI
    try:
        ctype = ClientType(client_type.upper())
    except:
        ctype = ClientType.OTHER
        
    client_id = presence_registry.register(ctype, "unknown").client_id
    logger.info(f"Client {client_id} connected via Stream.")
    event_bus.emit(EventType.CLIENT_CONNECTED, {"client_id": client_id})
    
    # Send initial state
    await websocket.send_json(get_current_state().model_dump())
    
    # Subscribe to Event Bus to push updates
    queue = asyncio.Queue()
    
    async def event_handler(data):
        await queue.put(data)
        
    # Subscribe to ALL events 
    event_bus.subscribe_async(EventType.SCHEDULER_TICK, event_handler)
    event_bus.subscribe_async(EventType.MISSION_STARTED, event_handler)
    event_bus.subscribe_async(EventType.MISSION_COMPLETED, event_handler)
    event_bus.subscribe_async(EventType.CLIENT_CONNECTED, event_handler)
    event_bus.subscribe_async(EventType.CLIENT_DISCONNECTED, event_handler)
    
    try:
        while True:
            # Wait for event
            event_data = await queue.get()
            
            # On event, generate FRESH state and send.
            state = get_current_state()
            await websocket.send_json(state.model_dump())
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected.")
        presence_registry.unregister(client_id)
        event_bus.emit(EventType.CLIENT_DISCONNECTED, {"client_id": client_id})
    except Exception as e:
        logger.error(f"Stream Error: {e}")
        presence_registry.unregister(client_id)
        event_bus.emit(EventType.CLIENT_DISCONNECTED, {"client_id": client_id})
