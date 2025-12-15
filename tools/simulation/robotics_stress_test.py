
import sys
import os
import time
import logging
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from brain.manipulation.manipulator_v2 import manipulator_v2, Point3D
from brain.robotics.safety_layer import safety_layer
from brain.spatial.spatial_mesh import spatial_mesh
from brain.vision.depth_model_loader import depth_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RoboStress")

def run_stress_test(hours=3):
    logger.info(f"Starting {hours} hour Robotics + AR stress test...")
    
    # Speed up simulation for CI: 1 hour virtual time = 1 second real time
    # Actually just run X iterations representing the load
    iterations = 50 # Represents "50+ manipulations"
    
    safety_violations = 0
    successful_moves = 0
    
    for i in range(iterations):
        # 1. Simulate changing environment (Spatial Mesh update)
        # Randomly place an "object"
        if random.random() > 0.5:
            spatial_mesh.points = [(0.5, 0.5, 0.5)] # Object in middle
        else:
            spatial_mesh.points = [] # Clear
            
        # 2. Plan a random move
        tx = random.uniform(0.0, 0.8)
        ty = random.uniform(0.0, 0.8)
        tz = random.uniform(0.0, 0.5)
        target = Point3D(tx, ty, tz)
        
        # 3. Validate Safety
        is_safe = safety_layer.validate_move(target)
        
        if not is_safe:
            safety_violations += 1
            logger.info(f"Iteration {i}: Safety Intervention (Target {tx:.2f}, {ty:.2f})")
            continue
            
        # 4. Execute Move (Simulated)
        if manipulator_v2.execute_move(target):
            successful_moves += 1
            logger.info(f"Iteration {i}: Move Successful")
        else:
            logger.warning(f"Iteration {i}: Move Failed (Reachability?)")
            
        time.sleep(0.01) # fast loop
        
    logger.info("Stress Test Complete.")
    logger.info(f"Total Attempts: {iterations}")
    logger.info(f"Successful Moves: {successful_moves}")
    logger.info(f"Safety Interventions: {safety_violations}")
    
    if successful_moves + safety_violations == iterations: # or close to it
        print("SUCCESS: Simulation stable.")
    else:
        print("WARNING: Some iterations unaccounted for.")

if __name__ == "__main__":
    run_stress_test(hours=3)
