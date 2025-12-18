import sys
import os
import time
from unittest.mock import MagicMock

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity

def verify_search():
    print("=== CONTEXTUAL SEARCH CHECK ===")
    
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
    
    # 1. Create Critical Signal (Should Trigger Search)
    print("\n--- Step 1: Create Critical Signal ---")
    sig_id = "sig_critical_search"
    mission_scheduler.external_observer.inject_mock_signal("Critical Data Leak", "security_feed", SignalSeverity.HIGH)
    # The injection generates a random ID, but we need to find it from the observer
    
    mission_scheduler.tick()
    
    # Use the signal from the observer
    if not mission_scheduler.external_observer._signals:
        print("FAIL: Signal not injected.")
        return
        
    sig = mission_scheduler.external_observer._signals[0]
    print(f"Signal ID: {sig.signal_id}")

    # Check Ledger for SEARCH
    entries = mission_scheduler.autonomy_ledger.get_entries()
    if any(e.decision_type == DecisionType.CONTEXTUAL_SEARCH_PERFORMED for e in entries):
        print("PASS: Ledger SEARCH_PERFORMED logged.")
    else:
        print(f"FAIL: Ledger missing SEARCH. Entries: {[e.decision_type for e in entries]}")
        
    # 2. Check API
    print("\n--- Step 2: Check API ---")
    client = TestClient(app)
    res = client.get(f"/contextual/search/{sig.signal_id}")
    
    if res.status_code == 200:
        data = res.json()
        print("PASS: API returned result.")
        print(f"Summary: {data['summary']}")
        print(f"Confidence: {data['confidence_score']}")
    else:
        print(f"FAIL: API Error {res.status_code}")

if __name__ == "__main__":
    verify_search()
