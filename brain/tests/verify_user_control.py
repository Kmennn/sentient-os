import sys
import os

sys.path.append(os.getcwd())

# Mock things being imported
from brain.missions.mission_scheduler import mission_scheduler
from brain.api.stream import set_interrupt_style
from brain.preferences.interrupt_style import InterruptStyle

# We can directly call the function used by the API endpoint to verify logic
# Since we can't spin up uvicorn easily.

def verify_control():
    print("=== USER CONTROL LOGIC CHECK ===")
    
    # 1. Check Initial
    print(f"Initial Style: {mission_scheduler.user_interrupt_settings.style}")
    
    # 2. Change Style via Scheduler (Simulating API)
    mission_scheduler.set_interrupt_style("never_interrupt")
    
    # 3. Verify Change
    current = mission_scheduler.user_interrupt_settings.style
    print(f"Changed Style: {current}")
    assert current == InterruptStyle.NEVER_INTERRUPT, "Style should update"
    
    # 4. Verify Persistence (Check Context Store directly)
    # We know save_user_context is called.
    # Let's peek at the file or the store object state if possible, but store loads from disk on init.
    # We can check mission_scheduler.user_context_store.file_path
    
    import json
    with open(mission_scheduler.user_context_store.file_path, 'r') as f:
        data = json.load(f)
        saved_style = data['interrupt_settings']['style']
        print(f"Persisted Style: {saved_style}")
        assert saved_style == "never_interrupt", "Style should be saved to disk"
        
    print("PASS: User control updates logic and persists.")

if __name__ == "__main__":
    verify_control()
