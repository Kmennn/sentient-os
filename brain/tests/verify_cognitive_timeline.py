import sys
import os
import time
import uuid
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType, AutonomyDecision

def verify_timeline():
    print("=== COGNITIVE TIMELINE CHECK ===")
    
    scheduler = mission_scheduler
    ledger = scheduler.autonomy_ledger
    builder = scheduler.timeline_builder
    
    # 1. Inject Events
    # Filter
    ledger.append(AutonomyDecision(
        str(uuid.uuid4()), DecisionType.ALERT_FILTERED_BY_PREFERENCE, time.time(), "Too noisy", True
    ))
    # Reflection
    ledger.append(AutonomyDecision(
        str(uuid.uuid4()), DecisionType.REFLECTION_NEGATIVE, time.time()+1, "Over-filtered SYSTEM", True
    ))
    # Adjustment
    ledger.append(AutonomyDecision(
        str(uuid.uuid4()), DecisionType.ADJUSTMENT_PROPOSED, time.time()+2, "Upgrade SYSTEM to MEDIUM", True
    ))
    
    # 2. Build
    events = builder.build_timeline(duration_seconds=3600)
    
    # 3. Verify
    print(f"Total Events: {len(events)}")
    if len(events) >= 3:
        print("PASS: Events captured.")
    else:
        print("FAIL: Events missing.")
        
    # Check Narration
    e_ref = next((e for e in events if "Reflected" in e.summary), None)
    if e_ref:
        print(f"Reflection Logic: {e_ref.agent} -> {e_ref.summary}")
        if e_ref.agent == "Analyst":
            print("PASS: Reflection attributed to Analyst.")
        else:
             print("FAIL: Agent attribution wrong.")
             
    e_adj = next((e for e in events if "Proposed adjustment" in e.summary), None)
    if e_adj:
        print(f"Adjustment Logic: {e_adj.agent} -> {e_adj.summary}")
        if e_adj.agent == "Governor":
            print("PASS: Adjustment attributed to Governor.")
        else:
            print("FAIL: Agent attribution wrong.")

if __name__ == "__main__":
    verify_timeline()
