import sys
import os
import time

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity

def verify_external():
    print("=== EXTERNAL SIGNAL CHECK ===")
    
    # Reset
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    
    # 1. Inject Mock
    print("Step 1: Injecting Signal...")
    mission_scheduler.external_observer.inject_mock_signal("Test Signal Alpha", "mock_feed", SignalSeverity.HIGH)
    
    # 2. Tick
    print("Step 2: Ticking Scheduler...")
    # Mock services to avoid crash
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    
    mission_scheduler.tick()
    
    # 3. Check Ledger
    print("Step 3: Checking Ledger...")
    entries = mission_scheduler.autonomy_ledger.get_entries()
    # Looking for EXTERNAL_SIGNAL_DETECTED
    found = any(e.decision_type == DecisionType.EXTERNAL_SIGNAL_DETECTED for e in entries)
    if not found:
        print("FAIL: Signal detection not logged in ledger.")
        return
    else:
        print("PASS: Signal logged in ledger.")
        
    # 4. Check API
    print("Step 4: Checking API...")
    client = TestClient(app)
    response = client.get("/external/signals")
    
    if response.status_code != 200:
        print(f"FAIL: API Error {response.status_code}")
        return
        
    data = response.json()
    if len(data) < 1:
        print("FAIL: No signals returned from API.")
        return
        
    sig = data[0]
    if sig['title'] == "Test Signal Alpha" and sig['severity'] == "high":
        print("PASS: API returned correct signal data.")
    else:
        print(f"FAIL: Data mismatch: {sig}")

if __name__ == "__main__":
    verify_external()
