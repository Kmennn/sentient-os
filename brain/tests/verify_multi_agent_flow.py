import sys
import os
import time
import uuid
from brain.reflection.reflection_event import ReflectionEvent, ReflectionEventType
from brain.autonomy.autonomy_ledger import DecisionType, AutonomyDecision
from brain.missions.mission_scheduler import mission_scheduler
from brain.agents.agent_context import OBSERVER_CONTEXT, ANALYST_CONTEXT, GOVERNOR_CONTEXT

def verify_multi_agent():
    print("=== MULTI-AGENT BOUNDARY CHECK ===")
    
    scheduler = mission_scheduler
    ref_engine = scheduler.reflection_engine
    adj_engine = scheduler.adjustment_engine
    ledger = scheduler.autonomy_ledger
    
    ledger._entries = [] # Clear logic
    
    # 1. Test Valid Flows
    print("\n--- Step 1: Valid Flows ---")
    
    # Analyst -> Reflection
    print("Testing Analyst -> Reflection...")
    ref_engine.process_event(ReflectionEvent(ReflectionEventType.ALERT_SHOWN, "TEST", "1"), context=ANALYST_CONTEXT)
    # Check buffer
    if len(ref_engine.event_buffer) > 0:
        print("PASS: Analyst allowed to reflect.")
    else:
        print("FAIL: Analyst blocked.")
        
    # Governor -> Proposal (via scan_ledger)
    print("Testing Governor -> Proposal Scan...")
    adj_engine.scan_ledger_for_proposals([], context=GOVERNOR_CONTEXT)
    # No crash or violation log means pass (checking ledger for violation)
    entries = ledger.get_entries()
    violations = [e for e in entries if e.decision_type == DecisionType.AGENT_BOUNDARY_VIOLATION]
    if not violations:
        print("PASS: Governor allowed to scan.")
    else:
        print(f"FAIL: Governor blocked. {violations[-1].reason}")
        
    # 2. Test Invalid Flows
    print("\n--- Step 2: Invalid Flows (Boundary Violations) ---")
    ledger._entries = []
    
    # Observer -> Proposal
    print("Testing Observer -> Proposal Scan...")
    adj_engine.scan_ledger_for_proposals([], context=OBSERVER_CONTEXT)
    entries = ledger.get_entries()
    v = [e for e in entries if e.decision_type == DecisionType.AGENT_BOUNDARY_VIOLATION]
    if v and "OBSERVER" in v[-1].reason:
         print("PASS: Observer blocked from creating proposals.")
    else:
         print("FAIL: Observer NOT blocked.")

    # Governor -> Reflection
    print("Testing Governor -> Reflection...")
    ledger._entries = []
    ref_engine.process_event(ReflectionEvent(ReflectionEventType.ALERT_SHOWN, "TEST", "2"), context=GOVERNOR_CONTEXT)
    entries = ledger.get_entries()
    v = [e for e in entries if e.decision_type == DecisionType.AGENT_BOUNDARY_VIOLATION]
    if v and "GOVERNOR" in v[-1].reason:
         print("PASS: Governor blocked from reflecting.")
    else:
         print("FAIL: Governor NOT blocked.")

if __name__ == "__main__":
    verify_multi_agent()
