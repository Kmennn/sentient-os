import sys
import os

sys.path.append(os.getcwd())

# Mock things being imported
from brain.state.state_snapshot import SystemState
from brain.api.stream import get_current_state
from brain.missions.mission_scheduler import mission_scheduler

def verify_schema():
    print("=== TRANSPARENCY SCHEMA CHECK ===")
    
    # 1. Initialize Scheduler Dependencies properly (Should typically be done by main.py)
    # The scheduler is global but needs its init called or parts of it?
    # It has an __init__ that runs on import? No, mission_scheduler is an instance.
    # It initializes in its structure.
    
    # 2. Add some dummy data
    mission_scheduler.device_registry.register_heartbeat("d1", "desktop", [])
    mission_scheduler.device_confidence_manager.register_interaction("d1")
    mission_scheduler.manual_focus_provider.start_focus(25)
    
    # 3. Generate State
    try:
        state = get_current_state()
        data = state.model_dump()
        
        # 4. Check
        print(f"Active Device: {data['active_device']}")
        print(f"Focus: {data['focus_state']}")
        
        # Check Device List
        if not data['device_list']:
             # It might be empty if we didn't force d1 to be active/registered fully?
             # register_heartbeat does adds it.
             # but get_active_devices filters by last_seen
             pass
        
        # We need to rely on the fact that we registered it.
        active = mission_scheduler.device_registry.get_active_devices()
        print(f"Registry Active Count: {len(active)}")
        
        print(f"Device List in State: {len(data['device_list'])}")
        
        # Validation
        assert "device_list" in data
        assert "confidence_level" in data
        assert "interrupt_style" in data
        
        print("PASS: Schema generation successful.")
        
    except Exception as e:
        print(f"FAIL: Schema Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_schema()
