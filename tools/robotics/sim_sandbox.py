
import sys
import os
import time
import logging
import random
import threading

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from brain.robotics.robot_controller import robot_controller
from brain.spatial.spatial_mapper import spatial_mapper
try:
    from brain.autonomy.spatial_autonomy_engine import spatial_autonomy
except ImportError:
    spatial_autonomy = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimSandbox")

def print_status():
    pose = robot_controller.get_status()
    voxels = spatial_mapper.get_occupied_voxels()
    print(f"\n--- ROBOT STATUS ---")
    print(f"Pose: x={pose.get('x',0):.2f}, y={pose.get('y',0):.2f}, z={pose.get('z',0):.2f}")
    print(f"Map Voxels: {voxels}")
    print(f"Autonomy: {'Active' if spatial_autonomy and spatial_autonomy.active else 'Inactive'}")
    print("--------------------")

def run_sandbox():
    logger.info("Initializing Sandbox...")
    
    # Mock some map data
    spatial_mapper.voxel_map.mark_occupied(0.5, 0.5, 0.05)
    
    running = True
    while running:
        print("\nCommands: [s]tatus, [m]ove, [g]rasp, [r]elease, [a]utonomy on/off, [q]uit")
        cmd = input(">> ").strip().lower()
        
        if cmd == 'q':
            running = False
        elif cmd == 's':
            print_status()
        elif cmd == 'm':
            try:
                args = input("Enter x y z (e.g. 0.5 0.5 0.2): ").split()
                if len(args) == 3:
                    x, y, z = map(float, args)
                    robot_controller.reach_to(x, y, z)
                else:
                    print("Invalid args")
            except ValueError:
                print("Invalid format")
        elif cmd == 'g':
            robot_controller.grasp_object()
        elif cmd == 'r':
            robot_controller.release_object()
        elif cmd == 'a':
            if spatial_autonomy:
                if spatial_autonomy.active:
                    spatial_autonomy.stop_loop()
                else:
                    spatial_autonomy.start_loop()
                    # Spin autonomy in background for demo
                    threading.Thread(target=spatial_autonomy.tik_tok, daemon=True).start()
        else:
            print("Unknown command")
        
        # Simulate slight delay
        time.sleep(0.1)

if __name__ == "__main__":
    run_sandbox()
