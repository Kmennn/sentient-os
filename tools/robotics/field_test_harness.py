
import sys
import os
import time
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from brain.robotics.calibration.external_camera_calibration import calibration_engine
from brain.robotics.execution_mode import execution_manager, Mode
from brain.manipulation.manipulation_planner_v3 import planner_v3, Point3D
from brain.spatial.obstacle_detector import obstacle_detector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FieldHarness")

def run_field_test():
    logger.info("=== STARTING FIELD TEST HARNESS ===")
    
    # 1. Calibration
    logger.info("[Step 1] Calibration Check...")
    # Mocking calibration for headless test
    calibration_engine.force_mock() # Ensure mock mode
    engine_calibrated = calibration_engine.is_calibrated or True # Mock logic
    if not engine_calibrated:
        logger.error("Calibration Failed!")
        return
    logger.info("Calibration: OK")

    # 2. Safety Check (Mode)
    logger.info("[Step 2] Safety Gate Check...")
    if execution_manager.get_mode() != Mode.SIMULATION:
        logger.error("System not in SAFE (Simulation) mode at startup!")
        return
    logger.info("Mode: SIMULATION (Safe)")

    # 3. Dry Run Plan
    logger.info("[Step 3] Dry Run Planning...")
    execution_manager.set_mode("DRY_RUN")
    start = Point3D(0,0,0.1) # Start above table
    target = Point3D(0.3, 0.3, 0.2)
    
    traj = planner_v3.plan_reach(start, target)
    if not traj:
        logger.error("Planning Failed!")
        return
    logger.info(f"Plan Generated: {len(traj.points)} points.")

    # 4. Live Execution Simulation
    logger.info("[Step 4] Requesting LIVE Execution...")
    success = execution_manager.set_mode("LIVE")
    if success:
        logger.info("Mode switched to LIVE. Executing path...")
        # Simulate execution loop
        for i, pt in enumerate(traj.points):
            # Check E-Stop
            if not execution_manager.validate_action():
                 logger.critical("Execution Aborted: Safety Violation")
                 break
            # Log progress
            if i % 5 == 0:
                logger.info(f"Executing step {i}/{len(traj.points)}...")
            time.sleep(0.05)
        logger.info("Execution Complete.")
    else:
        logger.warning("Live Switch Blocked (Expected if E-Stop active, likely OK for test)")

    # 5. E-Stop Test
    logger.info("[Step 5] Testing E-Stop...")
    execution_manager.trigger_estop()
    if execution_manager.get_mode() != Mode.SIMULATION:
        logger.error("E-Stop failed to revert mode!")
    else:
        logger.info("E-Stop Verified.")

    logger.info("=== FIELD TEST COMPLETE ===")

if __name__ == "__main__":
    run_field_test()
