import sys
import os
import time

sys.path.append(os.getcwd())

from brain.missions.mission_scheduler import mission_scheduler
from brain.proactive.proactive_suggestion import SuggestionStatus

def verify_auto():
    print("=== AUTO EXECUTION CHECK ===")
    
    # Mock Services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    
    # Establish Safety Conditions
    from brain.preferences.interrupt_style import InterruptStyle
    mission_scheduler.user_interrupt_settings.style = InterruptStyle.ALWAYS_ASK
    mission_scheduler.set_presence_private()
    mission_scheduler.stop_focus_session()
    
    # Trust must be > 0.95
    if "test_dev" not in mission_scheduler.device_registry._devices:
         mission_scheduler.device_registry.register_heartbeat("test_dev", "desktop", [])
    d = mission_scheduler.device_registry._devices["test_dev"]
    d.trust_score = 0.98
    mission_scheduler.active_device_resolver.report_interaction("test_dev", "input")
    
    # 1. Build Trust History (Need 5 successes)
    # Cheat by accessing policy directly
    print("Step 1: Building History...")
    mission_scheduler.autonomy_policy._stats = {} # reset
    for _ in range(5):
        mission_scheduler.autonomy_policy.record_success("maintenance_scan")
        
    stats = mission_scheduler.autonomy_policy._get_stats("maintenance_scan")
    print(f"Stats: Success={stats.success_count}, Dismiss={stats.dismissal_count}")
    
    # 2. Trigger Insight
    print("Step 2: Triggering Insight...")
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.proactive_engine._generation_history = {} # clear rate limit
    mission_scheduler._active_mission = None
    
    # Force tick
    mission_scheduler.tick()
    
    # 3. Check Result
    # Suggestion should be in active_suggestions list?
    # Logic: process_insights returns newly created.
    # Logic loop in tick:
    #   if allowed -> execute -> update status -> emit event.
    # It does NOT remove it from active_suggestions list in engine (unless we explicitly do so).
    # So we should find it in the list with status AUTO_EXECUTED.
    
    suggestions = mission_scheduler.proactive_engine.active_suggestions
    if not suggestions:
        print("FAIL: No suggestion created.")
        return
        
    sg = suggestions[0]
    print(f"Suggestion Status: {sg.status}")
    
    if sg.status == SuggestionStatus.AUTO_EXECUTED:
        print("PASS: Auto-Execution Successful.")
    else:
        print("FAIL: Suggestion was not auto-executed.")
        # Debug why
        act_def = mission_scheduler.action_registry.get_action(sg.action_id)
        fs, _ = mission_scheduler.get_current_focus_state()
        ps, _ = mission_scheduler.get_current_presence_state()
        allowed, reason = mission_scheduler.autonomy_policy.may_auto_execute(
                        sg.action_id, act_def, d.trust_score, mission_scheduler.user_interrupt_settings.style, 
                        fs.value != "free", ps.value == "with_others"
                    )
        print(f"Policy Reason: {reason}")


    # 4. Verify Kill Switch (Optional)
    # Simulate a dismissal to kill eligibility
    print("Step 3: Simulate Dismissal")
    mission_scheduler.autonomy_policy.record_dismissal("maintenance_scan")
    
    # Trigger again
    mission_scheduler.proactive_engine._generation_history = {} 
    mission_scheduler.tick() # Trigger insight
    
    # Last one should be PENDING (not auto)
    sg_latest = mission_scheduler.proactive_engine.active_suggestions[-1]
    if sg_latest.status == SuggestionStatus.PENDING:
        print("PASS: Auto-Execution blocked by Dismissal history.")
    else:
        print(f"FAIL: Should be PENDING, got {sg_latest.status}")

if __name__ == "__main__":
    verify_auto()
