from dataclasses import dataclass
import time

@dataclass
class NarratedContext:
    signal_id: str
    summary_text: str
    confidence_level: float
    source_count: int
    generated_at: float = 0.0
    
    def __post_init__(self):
        if self.generated_at == 0.0:
            self.generated_at = time.time()
            
    def to_dict(self):
        return {
            "signal_id": self.signal_id,
            "summary_text": self.summary_text,
            "confidence_level": self.confidence_level,
            "source_count": self.source_count,
            "generated_at": self.generated_at
        }
