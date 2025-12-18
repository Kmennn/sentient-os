import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity

def verify_ack():
    print("=== EMERGENCY ACK CHECK ===")
    
    # Mock Services
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    mission_scheduler.get_confidence_info = MagicMock(return_value=(0.9, "high"))
    
    # Reset
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.emergency_manager._emergencies = {}
    
    # 1. Create Critical Signal
    print("\n--- Step 1: Create Critical Signal ---")
    mission_scheduler.external_observer.inject_mock_signal("System Failure", "monitor", SignalSeverity.HIGH) 
    # Must use HIGH severity and "failure" which implies system domain? 
    # Wait, System Rule: "cpu", "memory", "crash", "outage". "failure" not in list.
    # Security Rule: "security", "alert".
    # I'll use "Security Breach" to be sure it's critical.
    mission_scheduler.external_observer._signals = [] # clear previous mock
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    
    mission_scheduler.tick()
    
    # Verify Creation
    pending = mission_scheduler.emergency_manager.get_pending()
    if len(pending) == 1:
        print(f"PASS: Emergency Created (ID: {pending[0].emergency_id})")
        eid = pending[0].emergency_id
    else:
        print("FAIL: Emergency not created.")
        return

    # Check Ledger
    entries = mission_scheduler.autonomy_ledger.get_entries()
    if any(e.decision_type == DecisionType.EMERGENCY_ACK_CREATED for e in entries):
        print("PASS: Ledger ACK_CREATED logged.")
    else:
        print("FAIL: Ledger missing ACK_CREATED.")
        
    # 2. Time Travel: 6 minutes (Level 1)
    print("\n--- Step 2: Time Travel +5 min ---")
    future_time = time.time() + 360
    
    # Manually trigger check with future time
    escalated = mission_scheduler.emergency_manager.check_escalation(now=future_time)
    
    # Manually check scheduler logic (Scheduler.tick calls check_escalation with default time usually)
    # But we want to simulate scheduler seeing this. 
    # Since we can't easily mock time.time() globally for the whole system without patching,
    # We will just verify manager logic here, and trust scheduler calls it.
    
    if escalated and escalated[0].escalation_level == 1:
        print("PASS: Escalated to Level 1.")
    else:
        print(f"FAIL: Did not escalate. Level: {pending[0].escalation_level}")
        
    # 3. Time Travel: 16 minutes (Level 2)
    print("\n--- Step 3: Time Travel +16 min ---")
    future_time_2 = time.time() + 1000
    escalated_2 = mission_scheduler.emergency_manager.check_escalation(now=future_time_2)
    
    if escalated_2 and escalated_2[0].escalation_level == 2:
        print("PASS: Escalated to Level 2.")
    else:
         # Note: if it already escalated to 1, this call might return it again if logic creates event every change.
         # My logic: "if new_level > ack.escalation_level".
         # Since we updated the object in Step 2, this should work.
         print(f"fail? Level: {pending[0].escalation_level}")
         if pending[0].escalation_level == 2:
             print("PASS: Level is 2.")
         else:
             print("FAIL: Level is not 2.")

    # 4. API Acknowledge
    print("\n--- Step 4: API Acknowledge ---")
    client = TestClient(app)
    res = client.post(f"/emergency/{eid}/acknowledge")
    
    if res.status_code == 200:
        print("PASS: API Acknowledged.")
    else:
        print(f"FAIL: API Error {res.status_code}")
        
    # Verify cleared
    pending = mission_scheduler.emergency_manager.get_pending()
    if len(pending) == 0:
        print("PASS: Emergency List Cleared.")
    else:
        print("FAIL: Still pending.")

    # Check Ledger
    entries = mission_scheduler.autonomy_ledger.get_entries()
    if any(e.decision_type == DecisionType.EMERGENCY_ACKNOWLEDGED for e in entries):
        print("PASS: Ledger ACKNOWLEDGED logged.")
    else:
        print("FAIL: Ledger missing ACKNOWLEDGED.")

if __name__ == "__main__":
    verify_ack()
