
import logging
import json
import os
import numpy as np
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class CalibrationEngine:
    def __init__(self, calibration_file="data/calibration.json"):
        self.calibration_file = calibration_file
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rotation_vec = None
        self.translation_vec = None
        self.is_calibrated = False
        
        # Load existing if available
        self.load_profile()

    def force_mock(self):
        global CV2_AVAILABLE
        CV2_AVAILABLE = False


    def calibrate_intrinsics(self, image_points: List[np.ndarray], object_points: List[np.ndarray], image_size: Tuple[int, int]) -> float:
        """
        Compute Camera Matrix and Distortion Coefficients.
        Returns re-projection error.
        """
        if not CV2_AVAILABLE:
            logger.info("Calibration: CV2 missing. Using Mock Intrinsics.")
            self.camera_matrix = np.eye(3)
            self.dist_coeffs = np.zeros(5)
            self.is_calibrated = True
            return 0.0

        try:
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                object_points, image_points, image_size, None, None
            )
            self.camera_matrix = mtx
            self.dist_coeffs = dist
            self.is_calibrated = True
            return ret
        except Exception as e:
            logger.error(f"Intrinsics Error: {e}")
            return -1.0

    def compute_extrinsics(self, image_points: np.ndarray, world_points: np.ndarray) -> bool:
        """
        Compute Transform from Camera to World (using PnP).
        """
        if not CV2_AVAILABLE:
            logger.info("Calibration: CV2 missing. Using Mock Extrinsics.")
            self.rotation_vec = np.zeros((3,1))
            self.translation_vec = np.zeros((3,1))
            return True

        if self.camera_matrix is None:
            logger.error("Calibration: Intrinsics missing.")
            return False

        try:
            success, rvec, tvec = cv2.solvePnP(
                world_points, image_points, self.camera_matrix, self.dist_coeffs
            )
            if success:
                self.rotation_vec = rvec
                self.translation_vec = tvec
            return success
        except Exception as e:
            logger.error(f"Extrinsics Error: {e}")
            return False

    def project_point(self, world_point: Tuple[float, float, float]) -> Optional[Tuple[int, int]]:
        """
        Project World (x,y,z) -> Image (u,v).
        """
        if not self.is_calibrated and CV2_AVAILABLE:
            return None
            
        if not CV2_AVAILABLE:
            # Mock projection: just scale x,y
            return (int(world_point[0]*100 + 320), int(world_point[1]*100 + 240))

        try:
            pts = np.array([world_point], dtype=np.float32)
            imgpts, _ = cv2.projectPoints(
                pts, self.rotation_vec, self.translation_vec, 
                self.camera_matrix, self.dist_coeffs
            )
            return tuple(map(int, imgpts[0].ravel()))
        except Exception as e:
            logger.error(f"Projection Error: {e}")
            return None

    def save_profile(self):
        data = {
            "camera_matrix": self.camera_matrix.tolist() if self.camera_matrix is not None else [],
            "dist_coeffs": self.dist_coeffs.tolist() if self.dist_coeffs is not None else [],
            "rotation": self.rotation_vec.tolist() if self.rotation_vec is not None else [],
            "translation": self.translation_vec.tolist() if self.translation_vec is not None else []
        }
        os.makedirs(os.path.dirname(self.calibration_file), exist_ok=True)
        with open(self.calibration_file, 'w') as f:
            json.dump(data, f)
        logger.info(f"Calibration saved to {self.calibration_file}")

    def load_profile(self):
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    data = json.load(f)
                self.camera_matrix = np.array(data["camera_matrix"])
                self.dist_coeffs = np.array(data["dist_coeffs"])
                self.rotation_vec = np.array(data["rotation"])
                self.translation_vec = np.array(data["translation"])
                self.is_calibrated = True
                logger.info("Calibration profile loaded.")
            except Exception as e:
                logger.warning(f"Failed to load calibration: {e}")

calibration_engine = CalibrationEngine()
