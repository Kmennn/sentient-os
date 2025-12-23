import sys
import os
import asyncio
import logging

# Setup path
sys.path.append(os.getcwd())

# Mock Event Bus to avoid "No Loop" errors if we just import logic
from brain.events.event_bus import event_bus

# Import the functionality
from brain.api.stream import get_current_state
from brain.missions.mission_scheduler import mission_scheduler

def test_state_generation():
    print("--- Testing get_current_state() ---")
    try:
        # We need to initialize what scheduler needs?
        # It auto-inits in __init__.
        
        print("Calling get_current_state()...")
        state = get_current_state()
        print("Success!")
        print(state.model_dump_json(indent=2))
        return True
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Ensure event loop for any async inits (though scheduler __init__ is sync mostly)
    test_state_generation()
