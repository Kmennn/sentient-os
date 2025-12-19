import sys
import os
import time
from brain.reflection.reflection_event import ReflectionEvent, ReflectionEventType
from brain.autonomy.autonomy_ledger import DecisionType
from brain.missions.mission_scheduler import mission_scheduler

def verify_reflection():
    print("=== SELF-CORRECTION REFLECTION CHECK ===")
    
    engine = mission_scheduler.reflection_engine
    engine.event_buffer.clear()
    engine.insights = []
    ledger = mission_scheduler.autonomy_ledger
    ledger._entries = []
    
    # 1. Test Over-Filter (Filter -> Search)
    print("\n--- Step 1: Over-Filter Detection ---")
    # Simulate Filtered Alert
    evt1 = ReflectionEvent(ReflectionEventType.ALERT_FILTERED, "SYSTEM", "sys_1", timestamp=time.time())
    engine.process_event(evt1)
    
    # Simulate Search 1 sec later
    evt2 = ReflectionEvent(ReflectionEventType.USER_MANUAL_SEARCH, "SYSTEM", metadata={"query": "cpu"}, timestamp=time.time() + 1)
    engine.process_event(evt2)
    
    # Check Ledger
    entries = ledger.get_entries()
    neg = [e for e in entries if e.decision_type == DecisionType.REFLECTION_NEGATIVE]
    if neg and "Over-filtered" in neg[-1].reason:
        print("PASS: Detected Over-filtering (Search after Filter).")
    else:
        print("FAIL: Failed to detect Over-filtering.")
        
    # 2. Test Over-Noise (Show -> Dismiss)
    print("\n--- Step 2: Over-Noise Detection ---")
    ledger._entries = [] # Reset
    
    evt3 = ReflectionEvent(ReflectionEventType.ALERT_SHOWN, "SECURITY", "sec_1", timestamp=time.time())
    engine.process_event(evt3)
    
    evt4 = ReflectionEvent(ReflectionEventType.ALERT_DISMISSED, "SECURITY", "sec_1", timestamp=time.time() + 1)
    engine.process_event(evt4)
    
    entries = ledger.get_entries()
    neg = [e for e in entries if e.decision_type == DecisionType.REFLECTION_NEGATIVE]
    if neg and "Over-noise" in neg[-1].reason:
        print("PASS: Detected Over-noise (Dismiss after Show).")
    else:
        print("FAIL: Failed to detect Over-noise.")
        
    # 3. Test POSITIVE (Show -> Ack)
    print("\n--- Step 3: Positive Feedback ---")
    ledger._entries = []
    
    evt5 = ReflectionEvent(ReflectionEventType.ALERT_SHOWN, "FINANCE", "fin_1", timestamp=time.time())
    engine.process_event(evt5)
    
    evt6 = ReflectionEvent(ReflectionEventType.ALERT_ACKED, "FINANCE", "fin_1", timestamp=time.time() + 1)
    engine.process_event(evt6)
    
    entries = ledger.get_entries()
    pos = [e for e in entries if e.decision_type == DecisionType.REFLECTION_POSITIVE]
    if pos:
        print("PASS: Detected Positive Signal (Ack after Show).")
    else:
        print("FAIL: Failed to detect Positive signal.")

if __name__ == "__main__":
    verify_reflection()
