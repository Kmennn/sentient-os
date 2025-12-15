
import logging
import time
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass
from brain.robotics.robot_controller import robot_controller

logger = logging.getLogger(__name__)

@dataclass
class DemoPoint:
    timestamp: float
    x: float
    y: float
    z: float
    state: str # optional, e.g., "gripper_open"

class DemonstrationRecorder:
    """
    Records human-guided robot motions.
    """
    def __init__(self):
        self.robot = robot_controller
        self.is_recording = False
        self.recorded_path: List[DemoPoint] = []
        self._thread = None
        self.sampling_rate = 0.1 # 10Hz

    def start_recording(self):
        if self.is_recording:
            logger.warning("Recorder already active.")
            return
            
        logger.info("Recorder: Started.")
        self.is_recording = True
        self.recorded_path = []
        self._thread = threading.Thread(target=self._record_loop)
        self._thread.start()

    def stop_recording(self) -> List[DemoPoint]:
        if not self.is_recording:
            logger.warning("Recorder not active.")
            return []
            
        self.is_recording = False
        if self._thread:
            self._thread.join()
            
        logger.info(f"Recorder: Stopped. Captured {len(self.recorded_path)} points.")
        return self.recorded_path

    def _record_loop(self):
        while self.is_recording:
            pose = self.robot.get_status()
            if pose:
                pt = DemoPoint(
                    timestamp=time.time(),
                    x=pose.get("x", 0.0),
                    y=pose.get("y", 0.0),
                    z=pose.get("z", 0.0),
                    state="unknown" # v2.8: gripper state
                )
                self.recorded_path.append(pt)
            
            time.sleep(self.sampling_rate)

demonstration_recorder = DemonstrationRecorder()
