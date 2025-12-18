import sys
import os
import time

sys.path.append(os.getcwd())

from brain.missions.mission_scheduler import mission_scheduler
from brain.ambient.ambient_insight import InsightType
from brain.proactive.proactive_suggestion import SuggestionStatus

def verify_suggestions():
    print("=== PROACTIVE SUGGESTION CHECK ===")
    
    # Reset
    mission_scheduler.ambient_observer.insights = []
    mission_scheduler.proactive_engine.active_suggestions = []
    mission_scheduler.proactive_engine._generation_history = {} # Clear rate limit
    
    # Mock Services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    # Suggestion Engine is REAL now, not mocked.
    
    # 1. Trigger IDLE Insight
    print("Step 1: Triggering Insight...")
    # Add fake device properly
    if "test_dev" not in mission_scheduler.device_registry._devices:
         mission_scheduler.device_registry.register_heartbeat("test_dev", "desktop", [])
    
    d = mission_scheduler.device_registry._devices["test_dev"]
    d.trust_score = 0.95
    mission_scheduler.active_device_resolver.report_interaction("test_dev", "input")
    mission_scheduler._active_mission = None
    mission_scheduler.stop_focus_session() # Free focus
    
    mission_scheduler.tick()
    
    # Check Insight
    insights = mission_scheduler.ambient_observer.insights
    if not insights:
        print("FAIL: No insights generated.")
        return
        
    print(f"Insights: {len(insights)}")
    
    # Check Suggestions (Engine should have picked it up)
    suggestions = mission_scheduler.proactive_engine.active_suggestions
    if not suggestions:
        print("FAIL: Engine did not generate suggestion.")
        return
        
    sg = suggestions[0]
    print(f"Suggestion Generated: [{sg.type.name}] {sg.message}")
    
    # Ensure Gating conditions are met
    from brain.preferences.interrupt_style import InterruptStyle
    mission_scheduler.user_interrupt_settings.style = InterruptStyle.ALWAYS_ASK
    mission_scheduler.set_presence_private()
    
    # 2. Check Display Gating (Should be allowed)
    displayable = mission_scheduler.get_displayable_suggestions()
    if not displayable:
        print("FAIL: Suggestion blocked by gating (should be visible).")
        st, _ = mission_scheduler.get_current_focus_state()
        print(f"Focus: {st}")
        ps, _ = mission_scheduler.get_current_presence_state()
        print(f"Presence: {ps}")
        style = mission_scheduler.user_interrupt_settings.style
        print(f"Style: {style}")
    else:
        print("PASS: Suggestion is visible.")
        
    # 3. Simulate Dismissal
    print("Step 2: Dismissing...")
    mission_scheduler.resolve_proactive_suggestion(sg.suggestion_id, "DISMISS")
    
    if sg.status == SuggestionStatus.DISMISSED:
        print("PASS: Suggestion marked DISMISSED.")
    else:
        print(f"FAIL: Status is {sg.status}")
        
    # 4. Check Display Gating (Should be hidden now)
    displayable_after = mission_scheduler.get_displayable_suggestions()
    if displayable_after:
        print("FAIL: Dismissed suggestion still visible.")
    else:
        print("PASS: Dismissed suggestion hidden.")

if __name__ == "__main__":
    verify_suggestions()
