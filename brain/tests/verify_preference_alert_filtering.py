import sys
import os
import shutil
from unittest.mock import MagicMock
from brain.external.external_signal import ExternalSignal, SignalSeverity
from brain.external.external_signal_classification import SignalDomain, SignalRiskLevel
from brain.missions.mission_scheduler import mission_scheduler
from brain.preferences.explicit_preference import ImportanceLevel
from brain.autonomy.autonomy_ledger import DecisionType

def verify_filtering():
    print("=== PREFERENCE ALERT FILTERING CHECK ===")
    
    # Setup
    mission_scheduler.preference_store.min_display_threshold = ImportanceLevel.MEDIUM
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.autonomy_ledger._entries = []
    
    # 1. Set Preference: SYSTEM = LOW
    print("\n--- Step 1: Set SYSTEM = LOW (Should Filter) ---")
    mission_scheduler.preference_store.set_preference("system", ImportanceLevel.LOW)
    
    # Create SYSTEM Signal (Low Risk)
    # Using Adapter Logic (Simulated)
    # Inject Signal -> Logic -> Suggestion
    sig_sys = ExternalSignal(
        signal_id="sys_1", source="os", title="System Check", summary="All good", severity=SignalSeverity.LOW,
        domain=SignalDomain.SYSTEM, risk_level=SignalRiskLevel.LOW, confidence=1.0
    )
    # Manually create suggestion via adapter
    s_sys = mission_scheduler.external_adapter.to_suggestion(sig_sys)
    mission_scheduler.proactive_engine.active_suggestions.append(s_sys)
    
    # Check Filtering
    displayable = mission_scheduler.get_displayable_suggestions()
    
    if s_sys in displayable:
        print("FAIL: System Alert should be hidden (Low < Medium).")
    else:
        print("PASS: System Alert Hidden.")
        if s_sys.is_filtered:
             print("PASS: is_filtered is True.")
             print(f"Reason: {s_sys.filtered_reason}")
             
    # 2. Check Security CRITICAL (Should Show)
    print("\n--- Step 2: Security CRITICAL (Should Show) ---")
    
    sig_sec = ExternalSignal(
        signal_id="sec_1", source="av", title="Breach", summary="Panic", severity=SignalSeverity.HIGH,
        domain=SignalDomain.SECURITY, risk_level=SignalRiskLevel.CRITICAL, confidence=1.0
    )
    s_sec = mission_scheduler.external_adapter.to_suggestion(sig_sec)
    mission_scheduler.proactive_engine.active_suggestions.append(s_sec)
    
    displayable_2 = mission_scheduler.get_displayable_suggestions()
    
    if s_sec in displayable_2:
        print("PASS: Critical Security Alert is Visible.")
    else:
        print(f"FAIL: Critical Alert hidden! Reason: {s_sec.filtered_reason}")
        
    # 3. Ledger Check
    print("\n--- Step 3: Ledger Check ---")
    entries = mission_scheduler.autonomy_ledger.get_entries()
    filtered_events = [e for e in entries if e.decision_type == DecisionType.ALERT_FILTERED_BY_PREFERENCE]
    
    if len(filtered_events) > 0:
        print("PASS: Ledger contains ALERT_FILTERED event.")
    else:
        print("FAIL: Ledger missing filter event.")

if __name__ == "__main__":
    verify_filtering()
