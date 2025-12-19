import sys
import os
import time
from brain.sync.sync_state import SyncState
from brain.missions.mission_scheduler import mission_scheduler
from brain.preferences.preference_store import ImportanceLevel
from brain.autonomy.autonomy_ledger import DecisionType

def verify_sync():
    print("=== SYNC STATE ROUNDTRIP CHECK ===")
    
    scheduler = mission_scheduler
    exporter = scheduler.state_exporter
    importer = scheduler.state_importer
    
    # 1. Setup: Set local preference = LOW
    scheduler.preference_store.set_preference("SYNC_TEST", ImportanceLevel.LOW)
    
    # 2. Export
    print("\n--- Step 1: Exporting State ---")
    state = exporter.export_sync_state()
    print(f"Exported Keys: {list(state.preferences.keys())}")
    print(f"Exported: {state.preferences.get('SYNC_TEST')}")
    
    if state.preferences.get('SYNC_TEST') == "low":
        print("PASS: Exported correctly.")
    else:
        print("FAIL: Export mismatch.")
        
    # 3. Simulate External Change (Sync Update)
    print("\n--- Step 2: Simulating External Update (LOW -> HIGH) ---")
    state.preferences['SYNC_TEST'] = "high"
    state.meaning_memory['SYNC_TEST'] = 0.95
    state.device_id = "external_peer"
    
    # 4. Import
    print("\n--- Step 3: Importing State ---")
    importer.validate_and_import(state)
    
    # 5. Verify Local Update
    curr = scheduler.preference_store.get_explicit_preference("SYNC_TEST")
    print(f"New Local Preference: {curr.importance_level.value}")
    
    if curr.importance_level == ImportanceLevel.HIGH:
        print("PASS: Preference updated via Sync.")
    else:
        print("FAIL: Preference mismatch.")
        
    meaning = scheduler.meaning_memory.get_relevance("SYNC_TEST")
    print(f"New Local Meaning: {meaning}")
    if meaning == 0.95:
         print("PASS: Meaning updated via Sync.")
    else:
         print("FAIL: Meaning mismatch.")
         
    # 6. Check Ledger
    entries = scheduler.autonomy_ledger.get_entries()
    imports = [e for e in entries if e.decision_type == DecisionType.SYNC_STATE_IMPORT_ATTEMPT]
    if imports:
        print("PASS: Import event logged.")
    else:
        print("FAIL: No ledger event.")

if __name__ == "__main__":
    verify_sync()
