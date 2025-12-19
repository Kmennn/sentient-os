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

def verify_memory():
    print("=== CONTEXTUAL MEMORY CHECK ===")
    
    # Setup Paths
    test_db = "brain_data/test_context_memory.jsonl"
    mission_scheduler.contextual_memory.persistence_path = test_db
    
    # Clean previous run
    if os.path.exists(test_db):
        os.remove(test_db)
    mission_scheduler.contextual_memory._history = []
    
    # Mock Services
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    mission_scheduler.get_confidence_info = MagicMock(return_value=(0.9, "high"))
    
    # Reset Runtime
    mission_scheduler.external_observer._signals = []
    mission_scheduler.autonomy_ledger._entries = []
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.emergency_manager._emergencies = {}
    
    # 1. First Occurrence
    print("\n--- Step 1: First Occurrence (New) ---")
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    # Debug
    if mission_scheduler.external_observer._signals:
        s = mission_scheduler.external_observer._signals[0]
        print(f"DEBUG: Signal Risk: {s.risk_level}")
    
    # Verify Ledger
    entries = mission_scheduler.autonomy_ledger.get_entries()
    recorded = any(e.decision_type == DecisionType.CONTEXTUAL_MEMORY_STORED for e in entries) or any(e.decision_type == "contextual_memory_recorded" for e in entries) # Back compat check
    
    if recorded:
        print("PASS: Memory Stored.")
    else:
        print(f"FAIL: Memory Store Missing. Events: {[e.decision_type for e in entries]}")
        
    # Check Patterns
    client = TestClient(app)
    # Using 'Critical Security Breach' as title key
    res = client.get("/contextual/patterns/Critical Security Breach")
    if res.status_code == 200:
        data = res.json()
        print(f"Pattern 1: Count={data['count']} Trend={data['trend']}")
        if data['trend'] == 'new' or data['trend'] == 'stable': # 1 item is usually "new" or "stable" depending on logic
             print("PASS: pattern trend OK.")
    else:
        print(f"FAIL: API Error {res.status_code}")

    # 2. Second Occurrence
    print("\n--- Step 2: Second Occurrence ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    res = client.get("/contextual/patterns/Critical Security Breach")
    data = res.json()
    print(f"Pattern 2: Count={data['count']} Trend={data['trend']}")
    if data['count'] == 2:
        print("PASS: Count increased.")

    # 3. Third Occurrence (Increasing)
    print("\n--- Step 3: Third Occurrence ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    res = client.get("/contextual/patterns/Critical Security Breach")
    data = res.json()
    print(f"Pattern 3: Count={data['count']} Trend={data['trend']}")
    
    # Logic in analyzer: if c7 > (c30/4)*1.5. 3 > (3/4)*1.5 => 3 > 1.125. True.
    if data['trend'] == 'rising':
        print("PASS: Trend is Rising.")
    else:
        print(f"FAIL: Expected Rising, got {data['trend']}")
        
    # 4. Persistence
    if os.path.exists(test_db):
        pass # OK
    else:
        print("FAIL: DB File Missing.")

    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)

if __name__ == "__main__":
    verify_memory()
