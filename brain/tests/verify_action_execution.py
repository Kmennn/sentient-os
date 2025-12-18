import sys
import os
import time

sys.path.append(os.getcwd())

from brain.missions.mission_scheduler import mission_scheduler
from brain.proactive.proactive_suggestion import SuggestionStatus

def verify_execution():
    print("=== ACTION EXECUTION CHECK ===")
    
    # Reset
    mission_scheduler.ambient_observer.insights = []
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.proactive_engine._generation_history = {}
    
    # Mock Services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    
    # Setup Safe Environment
    from brain.preferences.interrupt_style import InterruptStyle
    mission_scheduler.user_interrupt_settings.style = InterruptStyle.ALWAYS_ASK
    mission_scheduler.set_presence_private()
    mission_scheduler.stop_focus_session()
    
    # 1. Trigger IDLE
    if "test_dev" not in mission_scheduler.device_registry._devices:
         mission_scheduler.device_registry.register_heartbeat("test_dev", "desktop", [])
    d = mission_scheduler.device_registry._devices["test_dev"]
    d.trust_score = 0.95
    mission_scheduler.active_device_resolver.report_interaction("test_dev", "input")
    mission_scheduler._active_mission = None
    
    mission_scheduler.tick()
    
    # Get Suggestion
    suggestions = mission_scheduler.proactive_engine.active_suggestions
    if not suggestions:
        print("FAIL: No suggestion.")
        return
        
    sg = suggestions[0]
    print(f"Suggestion: {sg.action_id} | {sg.message}")
    
    if sg.action_id != "maintenance_scan":
        print("FAIL: Action ID missing or wrong.")
        return
        
    # 2. Accept and Execute
    print("Step 2: Accepting...")
    mission_scheduler.resolve_proactive_suggestion(sg.suggestion_id, "ACCEPT")
    
    if sg.status != SuggestionStatus.ACCEPTED:
        print("FAIL: Status not ACCEPTED.")
        
    # Check output logs manually for "[ACTION] Performing Maintenance Scan..." or mock executor
    # We can inspect the registry action executor call count if we mock it?
    # Or just rely on stdout for this script.
    
    # 3. Test Blocking mechanism
    print("Step 3: Test Blocking (Focus Active)")
    mission_scheduler.proactive_engine.active_suggestions = [] # clear
    mission_scheduler.proactive_engine._generation_history = {} # clear
    
    # Trigger again
    mission_scheduler.tick()
    sg2 = mission_scheduler.proactive_engine.active_suggestions[0]
    
    # Set Focus
    mission_scheduler.start_focus_session(25)
    
    # Try Accept
    mission_scheduler.resolve_proactive_suggestion(sg2.suggestion_id, "ACCEPT")
    
    # Verify status (Engine marks accepted, but Scheduler blocks execution)
    # The current logic updates status to ACCEPTED then checks gates for EXECUTION.
    # So status is ACCEPTED, but Action shouldn't run.
    print(f"Status: {sg2.status}")

if __name__ == "__main__":
    verify_execution()
