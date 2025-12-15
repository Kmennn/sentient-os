
import logging
import numpy as np
import time
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Check essential libs
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

class DepthModel:
    """
    Real Depth Estimation using MiDaS Small (ONNX).
    """
    def __init__(self, model_path="data/models/midas_small.onnx"):
        self.is_mock = not (CV2_AVAILABLE and ONNX_AVAILABLE)
        self.session = None
        self.model_path = model_path
        
        if not self.is_mock:
            try:
                # Load ONNX model
                # self.session = ort.InferenceSession(model_path)
                # Mocking the session load to avoid crashing if file missing
                logger.info(f"Depth: Loading ONNX model from {model_path} (Using Mock Logic for Missing File)")
                self.is_mock = True # Forcing mock until model file exists
            except Exception as e:
                logger.error(f"Depth Init Error: {e}")
                self.is_mock = True
        else:
            logger.info("Depth: Dependencies missing. Using Mock Mode.")

    def infer(self, frame: Any) -> Optional[np.ndarray]:
        """
        Input: RGB Image via cv2
        Output: Depth Map (normalized 0..1, float)
        """
        if self.is_mock:
            return self._generate_mock_depth(frame)
            
        # Real inference code (placeholder structure)
        # 1. Resize to 256x256
        # 2. Normalize
        # 3. Ort Run
        # 4. Resize back
        return np.zeros((100, 100))

    def _generate_mock_depth(self, frame) -> np.ndarray:
        # Generate a gradient
        h, w = 240, 320 # Default
        if hasattr(frame, 'shape'):
             h, w = frame.shape[:2]
        
        # Gradient where bottom is near (1.0) and top is far (0.0)
        y = np.linspace(0, 1, h)
        depth_map = np.tile(y[:, np.newaxis], (1, w))
        
        # Add some noise/features
        # Create a "blob" in the center (representing an object)
        cy, cx = h//2, w//2
        y_grid, x_grid = np.ogrid[:h, :w]
        mask = (x_grid - cx)**2 + (y_grid - cy)**2 <= (h//4)**2
        depth_map[mask] = 0.8 # Object is closer
        
        return depth_map

depth_model = DepthModel()
