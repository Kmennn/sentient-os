import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.getcwd())

from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity

def verify_narration():
    print("=== CONTEXTUAL NARRATION CHECK ===")
    
    # Mock Services
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    mission_scheduler.get_confidence_info = MagicMock(return_value=(0.9, "high"))
    
    # Reset
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.emergency_manager._emergencies = {}
    mission_scheduler.contextual_search._results = {}
    mission_scheduler.contextual_narrator._narrations = {}
    
    # 1. Create Critical Signal
    print("\n--- Step 1: Create Critical Signal ---")
    mission_scheduler.external_observer.inject_mock_signal("Critical Database Failure", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    if not mission_scheduler.external_observer._signals:
        print("FAIL: Signal not injected.")
        return
        
    sig = mission_scheduler.external_observer._signals[0]
    print(f"Signal ID: {sig.signal_id}")

    # Check Ledger
    entries = mission_scheduler.autonomy_ledger.get_entries()
    has_search = any(e.decision_type == DecisionType.CONTEXTUAL_SEARCH_PERFORMED for e in entries)
    has_narration = any(e.decision_type == DecisionType.CONTEXTUAL_NARRATION_GENERATED for e in entries)
    
    if has_search and has_narration:
        print("PASS: Ledger contains both SEARCH and NARRATION.")
    else:
        print(f"FAIL: Ledger missing events. Types: {[e.decision_type for e in entries]}")
        
    # 2. Check API
    print("\n--- Step 2: Check API ---")
    client = TestClient(app)
    res = client.get(f"/contextual/narration/{sig.signal_id}")
    
    if res.status_code == 200:
        data = res.json()
        print("PASS: API returned Narration.")
        print(f"Summary: {data['summary_text']}")
        print(f"Confidence: {data['confidence_level']}")
        
        # Verify Tone
        txt = data['summary_text']
        if "Analysis of" in txt and "No automated actions" in txt:
            print("PASS: Tone is neutral and informative.")
        else:
            print("FAIL: Tone check failed.")
    else:
        print(f"FAIL: API Error {res.status_code}")

    # 3. Stream Check
    print("\n--- Step 3: Check Stream Flag ---")
    # We can check the internal state since we can't easily poll WS in this script
    state = mission_scheduler.contextual_narrator.get_narration(sig.signal_id)
    if state:
        print("PASS: Narration is present in internal state.")
    
    # Check if stream would return true
    has_narration_flag = len(mission_scheduler.contextual_narrator._narrations) > 0
    if has_narration_flag:
        print("PASS: Stream flag logic is True.")
    else:
        print("FAIL: Stream flag logic is False.")

if __name__ == "__main__":
    verify_narration()
