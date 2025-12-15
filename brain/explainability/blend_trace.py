
import logging
from dataclasses import dataclass, asdict
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class BlendTraceRecord:
    parameter: str
    base_value: float
    policy_delta: float
    alpha: float
    final_value: float
    notes: str = ""

class BlendTrace:
    """
    Records why a blending decision was made.
    """
    def generate_trace(self, record: BlendTraceRecord) -> str:
        """
        Returns human-readable explanation.
        """
        policy_contrib = record.policy_delta * (1.0 - record.alpha)
        
        msg = (
            f"Trace [{record.parameter}]: "
            f"Planner({record.base_value:.2f}) + "
            f"Policy({record.policy_delta:+.2f} * {1-record.alpha:.0%}) "
            f"-> Final({record.final_value:.2f})"
        )
        if record.notes:
            msg += f" [{record.notes}]"
            
        logger.info(msg)
        return msg

blend_trace = BlendTrace()
