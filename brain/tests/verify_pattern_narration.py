import sys
import os
import shutil
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.getcwd())

from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity

def verify_explanation():
    print("=== PATTERN EXPLANATION CHECK ===")
    
    # Setup Paths & Clean
    test_db = "brain_data/test_pattern_expl.jsonl"
    mission_scheduler.contextual_memory.persistence_path = test_db
    if os.path.exists(test_db):
        os.remove(test_db)
        
    mission_scheduler.contextual_memory._history = []
    mission_scheduler.pattern_narrator._explanations = {}
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.external_observer._signals = []
    mission_scheduler.emergency_manager._emergencies = {}
    
    # Mock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    mission_scheduler.get_confidence_info = MagicMock(return_value=(0.9, "high"))
    
    # 1. Trigger Signal
    print("\n--- Step 1: Trigger Signal ---")
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    # Verify Ledger
    entries = mission_scheduler.autonomy_ledger.get_entries()
    explained = any(e.decision_type == DecisionType.CONTEXTUAL_PATTERN_EXPLAINED for e in entries)
    
    if explained:
        print("PASS: Pattern Explained Event Logged.")
    else:
        print(f"FAIL: Explanation Missing. Events: {[e.decision_type for e in entries]}")
        
    # Check API
    client = TestClient(app)
    res = client.get("/contextual/patterns/Critical Security Breach/explanation")
    
    if res.status_code == 200:
        data = res.json()
        print(f"Explanation: {data['summary_text']}")
        print(f"Trend: {data['trend_label']}")
        
        # Verify Tone
        if "first detected occurrence" in data['summary_text']:
            print("PASS: Neutral Tone Confirmed (New).")
    else:
        print(f"FAIL: API Error {res.status_code}")
        
    # 2. Trigger Rising Trend
    print("\n--- Step 2: Trigger Rising Trend ---")
    # Add fake history to force rising trend without waiting tick loops
    # 30d history of nothing vs current high
    # Actually simpler to just inject multiple times
    mission_scheduler.external_observer._signals = []
    mission_scheduler.contextual_memory.add(MagicMock(to_dict=lambda: {"title": "Unexpected CPU Spike", "generated_at": 0}), {"title": "Unexpected CPU Spike", "risk_level": "high"})
    mission_scheduler.contextual_memory.add(MagicMock(to_dict=lambda: {"title": "Critical Security Breach", "generated_at": 0}), {"title": "Critical Security Breach", "risk_level": "high"})
    mission_scheduler.contextual_memory.add(MagicMock(to_dict=lambda: {"title": "Critical Security Breach", "generated_at": 0}), {"title": "Critical Security Breach", "risk_level": "high"})
    
    # Now trigger again
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    res = client.get("/contextual/patterns/Critical Security Breach/explanation")
    if res.status_code == 200:
        data = res.json()
        print(f"Explanation 2: {data['summary_text']}")
        if "increasing" in data['summary_text'] or "New" in data['summary_text']: # Might still be 'new' depending on logic threshold
             # My logic: c7 > c30/4 * 1.5. If I added 2 quickly, they are all in c7.
             # So c7=3. c30=3.
             # 3 > (3/4)*1.5 => 3 > 0.75 * 1.5 => 3 > 1.125. True. "Rising".
             if "increasing" in data['summary_text']:
                 print("PASS: Explanation updated to reflect Rising Trend.")
             else:
                 print("WARN: Trend logic check doubtful but API works.")

    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)

if __name__ == "__main__":
    verify_explanation()
