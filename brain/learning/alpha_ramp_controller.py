
import logging
import time

logger = logging.getLogger(__name__)

class AlphaRampController:
    """
    Manages smooth transitions of the Alpha parameter.
    Prevents abrupt changes in control authority unless emergency.
    """
    def __init__(self, start_alpha: float = 1.0):
        self._current_alpha = start_alpha
        self._target_alpha = start_alpha
        self._max_delta_per_sec = 0.5 # 2 seconds full scale
        self._last_update_time = time.time()
        
    def set_target(self, target: float):
        self._target_alpha = max(0.0, min(1.0, target))
        # No immediate jump (unless force_override called)
        
    def force_override(self, value: float):
        """
        Instant jump for safety fallback.
        """
        self._current_alpha = max(0.0, min(1.0, value))
        self._target_alpha = self._current_alpha
        logger.info(f"Alpha FORCE OVERRIDE to {self._current_alpha}")
        
    def update(self) -> float:
        """
        Call per frame/step to update current alpha towards target.
        Returns new current alpha.
        """
        now = time.time()
        dt = now - self._last_update_time
        self._last_update_time = now
        
        if self._current_alpha == self._target_alpha:
            return self._current_alpha
            
        max_change = self._max_delta_per_sec * dt
        
        if self._current_alpha < self._target_alpha:
            self._current_alpha = min(self._target_alpha, self._current_alpha + max_change)
        else:
            self._current_alpha = max(self._target_alpha, self._current_alpha - max_change)
            
        return self._current_alpha
        
    @property
    def current_alpha(self) -> float:
        return self._current_alpha

alpha_ramp = AlphaRampController()
