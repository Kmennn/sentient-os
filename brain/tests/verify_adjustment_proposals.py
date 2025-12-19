import sys
import os
import time
import uuid
from brain.reflection.reflection_event import ReflectionEvent, ReflectionEventType
from brain.autonomy.autonomy_ledger import DecisionType, AutonomyDecision
from brain.missions.mission_scheduler import mission_scheduler
from brain.preferences.explicit_preference import ImportanceLevel

def verify_adjustments():
    print("=== ADJUSTMENT PROPOSAL CHECK ===")
    
    scheduler = mission_scheduler
    engine = scheduler.adjustment_engine
    ledger = scheduler.autonomy_ledger
    
    # 1. Setup: System Pref = LOW
    scheduler.preference_store.set_preference("SYSTEM", ImportanceLevel.LOW)
    print("Set SYSTEM = LOW")
    
    # 2. Inject 3 Negative Reflections (Over-filter)
    # Since we scan ledger, we must inject into ledger directly or via ReflectionEngine.
    # We'll inject directly into Ledger for speed, simulating what ReflectionEngine would do.
    
    print("\n--- Step 1: Injecting 3 Negative Reflections ---")
    for i in range(3):
        d = AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=DecisionType.REFLECTION_NEGATIVE,
            timestamp=time.time(),
            reason="Over-filtered? User searched for 'SYSTEM'...",
            was_auto=True
        )
        ledger.append(d)
        
    # 3. Trigger Scan
    print("\n--- Step 2: Triggering Scan ---")
    entries = ledger.get_entries()[-10:]
    engine.scan_ledger_for_proposals(entries)
    
    # 4. Check Proposal
    proposals = [p for p in engine.active_proposals.values() if p.domain == "SYSTEM"]
    if not proposals:
        print("FAIL: No proposal created.")
        return
        
    prop = proposals[0]
    print(f"Proposal Created: {prop.domain} {prop.current_importance.value} -> {prop.proposed_importance.value}")
    
    if prop.proposed_importance == ImportanceLevel.MEDIUM:
        print("PASS: Proposal direction correct (Increase).")
    else:
        print(f"FAIL: Wrong proposal {prop.proposed_importance}")
        
    # 5. Approve
    print("\n--- Step 3: Approving Proposal ---")
    engine.approve_proposal(prop.proposal_id)
    
    if prop.status.value == "approved":
        print("PASS: Proposal marked approved.")
    else:
        print("FAIL: Status not updated.")
        
    # 6. Verify Store Update
    new_pref = scheduler.preference_store.get_explicit_preference("SYSTEM")
    print(f"New Preference Level: {new_pref.importance_level.value}")
    
    if new_pref.importance_level == ImportanceLevel.MEDIUM:
        print("PASS: Preference Store Updated.")
    else:
        print("FAIL: Store not updated.")

if __name__ == "__main__":
    verify_adjustments()
