
import logging
import time
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class MotionModel:
    def __init__(self):
        self.acceleration = (0.0, 0.0, 9.8) # x, y, z (gravity)
        self.gyro = (0.0, 0.0, 0.0)
        self.last_update = time.time()
        self.state = "STATIONARY" 
        
    def update(self, accel: Tuple[float, float, float], gyro: Tuple[float, float, float]):
        self.acceleration = accel
        self.gyro = gyro
        self.last_update = time.time()
        self._infer_state()
        
    def _infer_state(self):
        # Infer movement from accel
        ax, ay, az = self.acceleration
        total_accel = (ax**2 + ay**2 + az**2) ** 0.5
        
        # Simple threshold for movement
        # 1g (9.8 or 1.0 depending on units, assume m/s^2)
        variance = abs(total_accel - 9.8)
        
        if variance > 2.0:
            self.state = "MOVING"
        elif variance > 0.5:
             self.state = "MICRO_MOVEMENTS"
        else:
             self.state = "STATIONARY"
             
    def get_orientation(self) -> str:
        # Check Z and Y for Portrait/Landscape/Flat
        ax, ay, az = self.acceleration
        
        if abs(az) > 8.0: return "FLAT" # Lying on table
        if abs(ay) > 8.0: return "PORTRAIT" # Upright
        if abs(ax) > 8.0: return "LANDSCAPE"
        return "UNKNOWN"

motion_model = MotionModel()
