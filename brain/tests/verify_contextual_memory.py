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
    recorded = any(e.decision_type == DecisionType.CONTEXTUAL_MEMORY_RECORDED for e in entries)
    if recorded:
        print("PASS: Memory Recorded.")
    else:
        print("FAIL: Memory Record Missing.")
        
    # Check History Stats for First Item
    sig_1 = mission_scheduler.external_observer._signals[0]
    hist = mission_scheduler.contextual_narrator.get_narration(sig_1.signal_id)
    print(f"Stats 1: 7d={hist.historical_occurrences_7d} Trend={hist.trend_label}")
    if hist.trend_label == "recurring" or hist.trend_label == "new":
         # Logic might return recurring if naive len=1?
         # My Logic: "elif len(matches) == 1: trend = 'recurring'"
         # Wait, if we haven't saved IT yet when calling analysis?
         # Ah, analysis is called BEFORE saving. So matches=0.
         # Logic: if len > 1... elif len == 1... else (implicit) trend="new"?
         # Let's check my code.
         # Code: `trend = "new"` (default init). `if len > 1... elif len == 1: trend = "recurring"`.
         # So if matches=0, trend="new".
         # However, matches list is built from `self.memory_store.get_history()`.
         # And we record AFTER analysis.
         # So first time matches=0. Trend="new".
         if hist.trend_label == "new":
             print("PASS: Trend is New.")
         else:
             print(f"FAIL: Expected New, got {hist.trend_label}")
    
    # 2. Second Occurrence (Recurring)
    print("\n--- Step 2: Second Occurrence (Recurring) ---")
    mission_scheduler.external_observer._signals = [] # clear signals list, but memory persists
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    sig_2 = mission_scheduler.external_observer._signals[0]
    hist_2 = mission_scheduler.contextual_narrator.get_narration(sig_2.signal_id)
    
    print(f"Stats 2: 7d={hist_2.historical_occurrences_7d} Trend={hist_2.trend_label}")
    
    # Now matches should calculate 1 (the previous one).
    # Since len(matches) == 1, trend should be "recurring".
    if hist_2.trend_label == "recurring":
        print("PASS: Trend is Recurring.")
    else:
        print(f"FAIL: Expected Recurring, got {hist_2.trend_label}")
        
    # 3. Third Occurrence (Increasing?)
    print("\n--- Step 3: Third Occurrence ---")
    mission_scheduler.external_observer._signals = []
    mission_scheduler.external_observer.inject_mock_signal("Critical Security Breach", "security_feed", SignalSeverity.HIGH)
    mission_scheduler.tick()
    
    sig_3 = mission_scheduler.external_observer._signals[0]
    hist_3 = mission_scheduler.contextual_narrator.get_narration(sig_3.signal_id)
    
    print(f"Stats 3: 7d={hist_3.historical_occurrences_7d} Trend={hist_3.trend_label}")
    # Matches = 2.
    # Count7d = 2. Count30d = 2.
    # Logic: `if count_7d > (count_30d / 4) * 1.5`
    # 2 > (2/4)*1.5 => 2 > 0.5 * 1.5 => 2 > 0.75. True.
    # So trend should be "increasing".
    
    if hist_3.trend_label == "increasing":
        print("PASS: Trend is Increasing.")
    else:
        print(f"FAIL: Expected Increasing, got {hist_3.trend_label}")
        
    # 4. Verify Persistence File
    if os.path.exists(test_db):
        print("PASS: Persistence file exists.")
        with open(test_db) as f:
            lines = f.readlines()
            print(f"File Lines: {len(lines)} (Expected 3)")
            if len(lines) == 3:
                print("PASS: Correct event count in file.")
    else:
        print("FAIL: File not created.")

    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)

if __name__ == "__main__":
    verify_memory()
