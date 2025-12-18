import sys
import os
import time

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity
from brain.proactive.proactive_suggestion import VisibilityLevel

def verify_emer():
    print("=== EMERGENCY VISIBILITY CHECK ===")
    
    # Mock Services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    mission_scheduler.get_confidence_info = MagicMock(return_value=(0.9, "high"))
    
    # 1. Normal High Risk + Focus (Should Block)
    print("\n--- Test 1: High Risk + Focus (Should Block) ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.proactive_engine.active_suggestions = []
    
    # Start Focus
    mission_scheduler.start_focus_session(25)
    
    # Inject High Risk (Not Critical)
    # Use MEDIUM severity so Classifier doesn't promote "security" to CRITICAL.
    mission_scheduler.external_observer.inject_mock_signal("Important Security Update", "security_feed", SignalSeverity.MEDIUM)
    mission_scheduler.tick()
    
    # Check Suggestions (Should be blocked by ExternalPolicy because FS != free)
    entries = mission_scheduler.autonomy_ledger.get_entries()
    blocked = [e for e in entries if e.decision_type == DecisionType.EXTERNAL_SUGGESTION_BLOCKED]
    
    if blocked:
        print("PASS: Non-Critical High Risk blocked during Focus.")
    else:
        # Check if created?
        created = [e for e in entries if e.decision_type == DecisionType.EXTERNAL_SUGGESTION_CREATED]
        if created:
             print("FAIL: Non-Critical High Risk created during Focus (Should be blocked).")
        else:
             print("FAIL: No decision logged?")

    # 2. Critical Risk + Focus (Should Bypass)
    print("\n--- Test 2: Critical Risk + Focus (Should Show) ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.proactive_engine.active_suggestions = []
    
    # Focus still active
    
    # Inject Critical
    # Note: "System Meltdown" with HIGH severity -> Critical Risk in Classifier (Rule 2)
    mission_scheduler.external_observer.inject_mock_signal("Critical System Meltdown", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    # Check Ledger for CREATED and EMERGENCY_GRANTED
    entries = mission_scheduler.autonomy_ledger.get_entries()
    granted = [e for e in entries if e.decision_type == DecisionType.EMERGENCY_VISIBILITY_GRANTED]
    created = [e for e in entries if e.decision_type == DecisionType.EXTERNAL_SUGGESTION_CREATED]
    
    if granted and created:
        print("PASS: Critical Risk Bypassed Focus.")
        print(f"Reason: {granted[0].reason}")
        
        # Check Visibility Level
        print(f"Active Suggestions in Engine: {len(mission_scheduler.proactive_engine.active_suggestions)}")
        if mission_scheduler.proactive_engine.active_suggestions:
            s0 = mission_scheduler.proactive_engine.active_suggestions[0]
            print(f"S0 Status: {s0.status.value}")
            print(f"S0 Visibility: {s0.visibility_level.value}")
            
        sugs = mission_scheduler.get_displayable_suggestions()
        print(f"Displayable Suggestions: {len(sugs)}")
        if sugs:
            print(f"Top Suggestion Vis: {sugs[0].visibility_level}")
            
        if sugs and sugs[0].visibility_level == VisibilityLevel.FORCE_VISIBLE:
             print("PASS: Suggestion is FORCE_VISIBLE.")
        else:
             print("FAIL: Suggestion not visible or not FORCE_VISIBLE.")
    else:
        print("FAIL: Critical Risk blocked.")
        print(f"Logs: {[e.decision_type for e in entries]}")


if __name__ == "__main__":
    verify_emer()
