
import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger("detect_engine")

class DetectEngine:
    """
    Enhanced detection engine using heuristics and optional ONNX model.
    """
    def __init__(self):
        self.onnx_path = os.getenv("OSD_DETECTOR_PATH")
        self.use_gpu = os.getenv("USE_GPU", "false").lower() == "true"
        self._load_model()

    def _load_model(self):
        if self.onnx_path and os.path.exists(self.onnx_path):
            logger.info(f"Loading ONNX model from {self.onnx_path} (GPU={self.use_gpu})...")
            # Stub: self.session = onnxruntime.InferenceSession(...)
            self.model_loaded = True
        else:
            logger.info("No ONNX model found. Using Heuristics.")
            self.model_loaded = False

    def detect(self, image_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect objects/context in image.
        """
        objects = []
        confidence = 1.0
        
        # 1. Heuristic: Active Window
        active_window = metadata.get("active_window", "")
        if active_window:
            app_type = self._classify_window(active_window)
            if app_type:
                objects.append(f"App:{app_type}")
        
        # 2. Heuristic: Source
        source = metadata.get("source", "unknown")
        
        # 3. Model Inference (Stub)
        if self.model_loaded:
            # Simulated result
            objects.append("Person")
            confidence = 0.85
            
        return {
            "objects": objects,
            "confidence": confidence,
            "summary": f"Scene showing {', '.join(objects) if objects else 'desktop'}"
        }

    def _classify_window(self, title: str) -> str:
        title = title.lower()
        if "chrome" in title or "edge" in title or "firefox" in title:
            return "Browser"
        if "code" in title or "pycharm" in title or "sublime" in title:
            return "IDE"
        if "explorer" in title or "finder" in title:
            return "FileExplorer"
        if "discord" in title or "slack" in title or "whatsapp" in title:
            return "ChatApp"
        return "UnknownApp"

detect_engine = DetectEngine()
