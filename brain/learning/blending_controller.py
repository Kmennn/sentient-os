
import logging
from typing import Dict, Optional
from brain.safety.advisory_guard import AdvisoryGuard, advisory_guard

logger = logging.getLogger(__name__)

class BlendingController:
    """
    Computes blended parameters between Planner (Base) and Policy (Advisory).
    Enforces Alpha control and Safety Constraints.
    """
    def __init__(self, guard: AdvisoryGuard = advisory_guard):
        self.guard = guard
        # Alpha: 1.0 = Pure Planner, 0.0 = Policy Authority
        self.default_alpha = 1.0 
        
    def compute_blend(self, param_name: str, base_value: float, policy_delta: float, alpha: float) -> float:
        """
        Computes blended value: Final = Base + (Delta * (1 - Alpha)).
        Clamps to safety constraints.
        """
        # 1. Compute Blended Value
        # If alpha=1.0, term is 0 -> Final = Base.
        # If alpha=0.0, term is Delta -> Final = Base + Delta.
        
        blend_component = policy_delta * (1.0 - alpha)
        final_value = base_value + blend_component
        
        # 2. Safety Check / Clamp
        # We check against guard. If unsafe, fallback to Base? 
        # Or clamp? Guard returns bool.
        # We should check if final_value is valid.
        
        limits = self.guard.constraints.get(param_name)
        if limits:
            min_v, max_v = limits["min"], limits["max"]
            if final_value < min_v or final_value > max_v:
                logger.warning(f"Blending unsafe ({final_value:.2f}). Clamping/Resetting.")
                # Strategy: fallback to Base if Base is safe, or clamp.
                # Usually Base is safe by definition of Planner.
                # Let's fallback to base for safety dominance.
                return base_value
                
        logger.info(f"Blend '{param_name}': Base={base_value} Delta={policy_delta} Alpha={alpha} -> Final={final_value:.3f}")
        return final_value

blending_controller = BlendingController()
