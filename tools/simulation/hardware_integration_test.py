
import sys
import os
import time
import logging
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import Real Hardware Wrappers (which might mock themselves)
from brain.perception.scene_interpreter_real import scene_interpreter_real
from local_kernel.audio.real_audio_stream import real_audio
from brain.embodiment.motion_model import motion_model
from brain.manipulation.manipulation_planner import manipulation_planner
from brain.robotics.robotics_interface import robot_interface
from brain.context.context_v10 import context_manager_v10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HardwareSim")

def run_simulation(hours=2):
    logger.info(f"Starting {hours} hour hardware embodiment simulation...")
    
    virtual_time = time.time()
    end_time = virtual_time + (hours * 3600)
    
    frames_processed = 0
    audio_events = 0
    manipulations = 0
    
    while virtual_time < end_time:
        virtual_time += 10 # 10s per step for this test
        
        # 1. Vision Feed
        events = scene_interpreter_real.process_live_frame()
        if events: frames_processed += 1
        
        # 2. Audio Feed
        audio_event = real_audio.analyze_stream()
        if audio_event:
            logger.info(f"Audio: {audio_event['label']} (Sim)")
            audio_events += 1
            
        # 3. Motion Stimulus
        if random.random() > 0.95:
             # Simulate picking up device
             logger.info("Motion: Device picked up")
             motion_model.update((0, 10, 5), (0,0,0))
        else:
             motion_model.update((0, 0, 9.8), (0,0,0))
             
        # 4. Robot/Manipulation
        if random.random() > 0.98:
             # Plan a grasp
             traj = manipulation_planner.plan_action("grasp", (100,100), (200,200))
             logger.info(f"Manipulation: Planned grasp ({len(traj.points)} pts)")
             
             # Execute on Robot Interface
             robot_interface.move_to((0.5, 0.5, 0.2))
             robot_interface.grasp()
             robot_interface.release()
             manipulations += 1
             
        # 5. Context Fusion Check
        snap = context_manager_v10.get_hardware_snapshot({}, [])
        if snap["motion"]["state"] == "MOVING":
             logger.info("Context: Confirmed MOVING state")
             
    logger.info("Simulation Complete.")
    logger.info(f"Frames: {frames_processed}, Audio Events: {audio_events}, Manipulations: {manipulations}")
    
    if frames_processed > 0:
        print("SUCCESS: Hardware pipeline processed data.")
    else:
        print("WARNING: Hardware pipeline was silent.")

if __name__ == "__main__":
    run_simulation(hours=2)
