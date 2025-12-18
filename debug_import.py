import sys
import os
sys.path.append(os.getcwd())

print("Attempting to import MissionScheduler...")
try:
    from brain.missions.mission_scheduler import MissionScheduler
    print("Import MissionScheduler: SUCCESS")
except Exception as e:
    print(f"Import MissionScheduler: FAILED - {e}")
    import traceback
    traceback.print_exc()

print("\nAttempting to import Test File...")
try:
    from brain.tests import test_scheduler_conflicts
    print("Import Test: SUCCESS")
except Exception as e:
    print(f"Import Test: FAILED - {e}")
    import traceback
    traceback.print_exc()
