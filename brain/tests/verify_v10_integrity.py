import time
import sys
import os

# Ensure we can import brain modules
sys.path.append(os.getcwd())

from brain.missions.mission_scheduler import MissionScheduler
from brain.devices.active_device import InteractionType

def verify_backend():
    print("=== STARTING BACKEND VERIFICATION (v10.4) ===")
    scheduler = MissionScheduler()
    
    # 1. Device Registration
    print("\n[Test 1] Device Registration")
    scheduler.register_device("desktop1", "desktop", ["TOAST", "PANEL"])
    scheduler.register_device("mobile1", "mobile", ["TOAST"])
    active_len = len(scheduler.device_registry.get_active_devices())
    assert active_len == 2, f"Expected 2 devices, got {active_len}"
    print("PASS: Registered 2 devices.")
    
    # 2. Active Device & Confidence (Desktop)
    print("\n[Test 2] Interaction & Confidence Boost")
    scheduler.report_interaction("desktop1", "input")
    dev_id, conf = scheduler.get_active_device_info()
    assert dev_id == "desktop1", f"Expected desktop1, got {dev_id}"
    score, level = scheduler.get_confidence_info()
    print(f"Desktop Score: {score} ({level})")
    assert score > 0.5, "Confidence should have boosted > 0.5"
    print("PASS: Interaction registered and confidence boosted.")
    
    # 3. Handoff Detection & Context Window
    print("\n[Test 3] Handoff & Context Creation")
    # Simulate switching to mobile
    scheduler.report_interaction("mobile1", "input")
    
    # Check Handoff
    handoff = scheduler.last_handoff
    assert handoff is not None, "Handoff should be detected"
    assert handoff.from_device_id == "desktop1"
    assert handoff.to_device_id == "mobile1"
    print(f"PASS: Handoff {handoff.from_device_id} -> {handoff.to_device_id}")
    
    # Check Context Window
    ctx_status = scheduler.context_window_manager.get_status()
    assert ctx_status["active"] is True, "Context windows should be active"
    assert ctx_status["source"] == "desktop1"
    print("PASS: Context Window active.")
    
    # 4. Handoff Message Routing
    print("\n[Test 4] Handoff Output Routing")
    last_targets = scheduler.last_output_targets
    last_chan = scheduler.last_output_channel
    print(f"Routed to: {last_targets} via {last_chan}")
    
    assert "mobile1" in last_targets, "Should target new device"
    assert "desktop1" not in last_targets, "Should NOT target old device"
    print("PASS: Routing correct.")
    
    # 5. Decay (Simulation)
    print("\n[Test 5] Confidence Decay")
    # Manually hack last update time to simulate passage of time for desktop
    # desktop1 was last touched a moment ago. Let's make it 20 mins ago.
    d_conf = scheduler.device_confidence_manager._get_or_create("desktop1")
    d_conf.last_update_ts -= (20 * 60) # 20 mins
    
    d_score = scheduler.device_confidence_manager.get_score("desktop1")
    print(f"Desktop Score after 20m: {d_score}")
    assert d_score < 0.5, "Score should have decayed"
    print("PASS: Decay verified.")
    
    # 6. Low Confidence Routing
    print("\n[Test 6] Low Confidence Routing")
    # Make mobile1 very low confidence
    m_conf = scheduler.device_confidence_manager._get_or_create("mobile1")
    m_conf.score = 0.1 # Very low
    m_conf.last_update_ts = time.time()
    
    # Trigger routing via scheduler internals (simulating a message)
    # Re-using internal router logic for test
    from brain.context.presence_state import PresenceState
    from brain.communication.tone_profile import ToneProfile
    
    active_devs = scheduler.device_registry.get_active_devices()
    chan, tgts = scheduler.output_router.route(
        PresenceState.ALONE, ToneProfile.NEUTRAL, False, False, active_devs, 
        active_device_id="mobile1", device_confidence=0.1
    )
    print(f"Low Conf Route: {chan}")
    assert chan.value == "suppressed", f"Expected suppressed, got {chan}"
    print("PASS: Low confidence suppressed.")

    print("\n=== ALL BACKEND TESTS PASSED ===")

if __name__ == "__main__":
    verify_backend()
