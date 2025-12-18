import sys
import os
import time

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity
from brain.external.external_signal_classification import SignalDomain, SignalRiskLevel

def verify_class():
    print("=== EXTERNAL CLASSFICATION CHECK ===")
    
    # Reset
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    
    # 1. Inject Security Signal
    print("Step 1: Injecting Security Signal...")
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach detected in Firewall", "security_feed", SignalSeverity.HIGH)
    
    # 2. Tick
    print("Step 2: Ticking Scheduler...")
    # Mock services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    
    mission_scheduler.tick()
    
    # 3. Check Ledger
    print("Step 3: Checking Ledger...")
    entries = mission_scheduler.autonomy_ledger.get_entries()
    found = any(e.decision_type == DecisionType.EXTERNAL_SIGNAL_CLASSIFIED for e in entries)
    if not found:
        print("FAIL: Classification not logged.")
        # Print actual types found
        print(f"Found types: {[e.decision_type for e in entries]}")
        return
    else:
        print("PASS: Signal classification logged.")
        print(f"Log Reason: {entries[-1].reason}")
        
    # 4. Check API
    print("Step 4: Checking API...")
    client = TestClient(app)
    response = client.get("/external/signals")
    
    if response.status_code != 200:
        print(f"FAIL: API Error {response.status_code}")
        return
        
    data = response.json()
    sig = data[0]
    
    print(f"Signal: {sig['title']}")
    print(f"Domain: {sig['domain']}")
    print(f"Risk: {sig['risk_level']}")
    
    if sig['domain'] == "security" and sig['risk_level'] == "critical":
        print("PASS: Classification Correct (Security/Critical).")
    else:
        print("FAIL: Classification incorrect.")

if __name__ == "__main__":
    verify_class()
