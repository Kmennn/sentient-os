import sys
import os
import time

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity

def verify_bridge():
    print("=== EXTERNAL BRIDGE CHECK ===")
    
    # Mock Services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    
    # Mock trust directly
    mission_scheduler.get_confidence_info = MagicMock(return_value=(0.9, "high"))
    
    # 1. Low Risk (Should Block)
    print("\n--- Test 1: Low Risk Signal ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.external_observer.inject_mock_signal("Low Viz Info", "test", SignalSeverity.LOW)
    mission_scheduler.tick()
    
    entries = mission_scheduler.autonomy_ledger.get_entries()
    blocked = [e for e in entries if e.decision_type == DecisionType.EXTERNAL_SUGGESTION_BLOCKED]
    if blocked and "Risk too low" in blocked[0].reason:
        print("PASS: Low risk blocked.")
    else:
        print(f"FAIL: Low risk not blocked correctly. Found: {[e.decision_type for e in entries]}")
        
    # 2. High Risk but Public (Should Block)
    print("\n--- Test 2: High Risk + Public ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.set_presence_public()
    
    # Classifier rules: "security" -> HIGH risk
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Alert", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    entries = mission_scheduler.autonomy_ledger.get_entries()
    blocked = [e for e in entries if e.decision_type == DecisionType.EXTERNAL_SUGGESTION_BLOCKED]
    if blocked and "User in Public" in blocked[0].reason:
        print("PASS: Public blocked.")
    else:
        print(f"FAIL: Public not blocked correctly. Reason: {blocked[0].reason if blocked else 'None'}")

    # 3. High Risk + Private (Should Create)
    print("\n--- Test 3: High Risk + Private ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.set_presence_private()
    mission_scheduler.stop_focus_session()
    
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Alert 2", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    entries = mission_scheduler.autonomy_ledger.get_entries()
    created = [e for e in entries if e.decision_type == DecisionType.EXTERNAL_SUGGESTION_CREATED]
    
    if created:
        print("PASS: Suggestion Created.")
        
        # Check API
        client = TestClient(app)
        res = client.get("/stream") # Or just check suggestions endpoint if one existed, but checking state is easier via stream or internal list
        suggestions = mission_scheduler.proactive_engine.active_suggestions
        sg = next((s for s in suggestions if "Security Alert 2" in s.message), None)
        if sg:
            print(f"Suggestion found in engine: {sg.message}")
        else:
            print("FAIL: Suggestion not in engine.")
    else:
        print(f"FAIL: Suggestion not created. Logs: {[e.reason for e in entries]}")


if __name__ == "__main__":
    verify_bridge()
