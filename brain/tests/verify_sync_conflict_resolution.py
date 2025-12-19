import sys
import os
import time
from brain.sync.sync_state import SyncState
from brain.missions.mission_scheduler import mission_scheduler
from brain.preferences.preference_store import ImportanceLevel
from brain.autonomy.autonomy_ledger import DecisionType
from brain.sync.sync_conflict import ConflictResolution
from brain.memory.user_meaning import UserMeaning

def verify_conflicts():
    print("=== SYNC CONFLICT RESOLUTION CHECK ===")
    
    scheduler = mission_scheduler
    store = scheduler.preference_store
    memory = scheduler.meaning_memory
    importer = scheduler.state_importer
    
    # 1. Setup Local State
    # Domain A: Local is NEWER (Timestamp +10s). Local=HIGH.
    store.set_preference("DOMAIN_A", ImportanceLevel.HIGH)
    # Hack timestamp to be future
    store._preferences["DOMAIN_A"].updated_at = time.time() + 100
    store._save()
    
    # Domain B: Local is OLDER. Local=LOW.
    store.set_preference("DOMAIN_B", ImportanceLevel.LOW)
    store._preferences["DOMAIN_B"].updated_at = time.time() - 100
    store._save()
    
    # Meaning C: Local=0.2. Remote=0.8.
    if "DOMAIN_C" not in memory._meanings:
        memory._meanings["DOMAIN_C"] = UserMeaning("DOMAIN_C", 0.2, 0, 0)
    else:
        memory._meanings["DOMAIN_C"].relevance_score = 0.2
        
    # 2. Construct Remote State
    remote_state = SyncState(
        timestamp=time.time(), # Now
        preferences={
            "DOMAIN_A": "low",    # Conflict. Local is newer (HIGH) -> Local Wins.
            "DOMAIN_B": "high"    # Conflict. Remote is newer (HIGH) -> Remote Wins.
        },
        meaning_memory={
            "DOMAIN_C": 0.8       # Conflict. Should Merge -> (0.2+0.8)/2 = 0.5
        },
        trust_score=0.5,
        agent_phase="idle",
        last_decision_id="none"
    )
    
    # 3. Release Sync
    print("\n--- Step 1: Importing with Conflicts ---")
    importer.validate_and_import(remote_state)
    
    # 4. Verify Results
    print("\n--- Step 2: Verifying Domain A (Local Newer) ---")
    pref_a = store.get_explicit_preference("DOMAIN_A")
    print(f"Domain A Level: {pref_a.importance_level.value}")
    if pref_a.importance_level == ImportanceLevel.HIGH:
        print("PASS: Local preference preserved (Newer).")
    else:
        print("FAIL: Domain A incorrect.")
        
    print("\n--- Step 3: Verifying Domain B (Remote Newer) ---")
    pref_b = store.get_explicit_preference("DOMAIN_B")
    print(f"Domain B Level: {pref_b.importance_level.value}")
    if pref_b.importance_level == ImportanceLevel.HIGH:
        print("PASS: Remote preference applied (Newer).")
    else:
        print("FAIL: Domain B incorrect.")
        
    print("\n--- Step 4: Verifying Domain C (Meaning Merge) ---")
    score_c = memory.get_relevance("DOMAIN_C")
    print(f"Domain C Score: {score_c}")
    if abs(score_c - 0.5) < 0.01:
        print("PASS: Meaning merged correctly.")
    else:
        print("FAIL: Meaning not merged.")
        
    # 5. Verify History/Ledger
    print("\n--- Step 5: Ledger & API Check ---")
    conflicts = scheduler.conflict_resolver.get_conflicts()
    print(f"Recorded Conflicts: {len(conflicts)}")
    if len(conflicts) >= 3:
        print("PASS: All conflicts recorded.")
    else:
        print("FAIL: Missing history.")

if __name__ == "__main__":
    verify_conflicts()
