import sys
import os
import time

sys.path.append(os.getcwd())

from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType

def verify_ledger():
    print("=== AUTONOMY LEDGER CHECK ===")
    
    # Reset Ledger File
    ledger_path = "brain/api/autonomy_ledger_test.json"
    if os.path.exists(ledger_path):
        os.remove(ledger_path)
        
    # Inject Test Path
    mission_scheduler.autonomy_ledger.persistence_path = ledger_path
    mission_scheduler.autonomy_ledger._entries = []

    # Reset System State
    mission_scheduler.ambient_observer.insights = []
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.proactive_engine._generation_history = {}
    
    from brain.preferences.interrupt_style import InterruptStyle
    mission_scheduler.user_interrupt_settings.style = InterruptStyle.ALWAYS_ASK
    mission_scheduler.set_presence_private()
    mission_scheduler.stop_focus_session()
    
    # Mock Services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    
    # 1. Trigger Insight (Should log SUGGESTED)
    print("Step 1: Generating Insight...")
    if "test_dev" not in mission_scheduler.device_registry._devices:
         mission_scheduler.device_registry.register_heartbeat("test_dev", "desktop", [])
         mission_scheduler.device_registry._devices["test_dev"].trust_score = 0.90 # Not high enough for auto yet
    
    mission_scheduler.active_device_resolver.report_interaction("test_dev", "input")
    mission_scheduler._active_mission = None
    mission_scheduler.tick()
    
    entries = mission_scheduler.autonomy_ledger.get_entries()
    print(f"Entries after Tick: {len(entries)}")
    if len(entries) < 1 or entries[-1].decision_type != DecisionType.SUGGESTED:
        print("FAIL: Did not log SUGGESTED.")
        return
        
    sg_id = entries[-1].suggestion_id
    
    # 2. Accept (Should log ACCEPTED)
    print("Step 2: Accepting...")
    mission_scheduler.resolve_proactive_suggestion(sg_id, "ACCEPT")
    
    entries = mission_scheduler.autonomy_ledger.get_entries()
    print(f"Entries after Accept: {len(entries)}")
    
    found_accepted = any(e.decision_type == DecisionType.ACCEPTED for e in entries)
    if not found_accepted:
        print("FAIL: Did not log ACCEPTED.")
        return
        
    # 3. Persistence Check
    print("Step 3: Checking Persistence...")
    # Create new ledger instance pointing to same file
    new_ledger = AutonomyLedger(persistence_path=ledger_path)
    loaded_entries = new_ledger.get_entries()
    
    print(f"Loaded Entries: {len(loaded_entries)}")
    if len(loaded_entries) != len(entries):
        print("FAIL: Persistence mismatch.")
    else:
        print("PASS: Ledger persisted and reloaded correctly.")
        print(f"First Entry Type: {loaded_entries[0].decision_type}")

if __name__ == "__main__":
    verify_ledger()
