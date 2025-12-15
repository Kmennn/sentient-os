
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class BiModalAttention:
    def __init__(self):
        self.weights = {"audio": 0.5, "visual": 0.5}
        
    def shift_attention(self, stimulus_type: str, intensity: float):
        if stimulus_type == "audio":
            self.weights["audio"] = min(0.9, self.weights["audio"] + intensity * 0.5)
            self.weights["visual"] = 1.0 - self.weights["audio"]
        elif stimulus_type == "visual":
            self.weights["visual"] = min(0.9, self.weights["visual"] + intensity * 0.5)
            self.weights["audio"] = 1.0 - self.weights["visual"]

    def get_focus(self) -> str:
        if self.weights["audio"] > 0.6: return "AUDIO_DOMINANT"
        if self.weights["visual"] > 0.6: return "VISUAL_DOMINANT"
        return "BALANCED"

attention_model = BiModalAttention()
