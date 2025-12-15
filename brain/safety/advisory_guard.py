
import logging
from brain.learning.policy_advisor import AdvisorySuggestion

logger = logging.getLogger(__name__)

class AdvisoryGuard:
    """
    Gates advisory suggestions against hard safety constraints.
    """
    def __init__(self):
        self.constraints = {
            "lift_height": {"min": 0.0, "max": 0.3}, # Max 30cm lift
            "speed_scalar": {"min": 0.1, "max": 1.0}
        }

    def validate_suggestion(self, suggestion: AdvisorySuggestion, current_values: dict) -> bool:
        """
        Returns True if applying suggestion is safe.
        """
        param = suggestion.parameter
        
        if param not in self.constraints:
            logger.warning(f"Unknown parameter '{param}'. Rejecting suggestion.")
            return False
            
        current_val = current_values.get(param, 0.05) # Default 5cm
        proposed_val = current_val + suggestion.delta
        
        limits = self.constraints[param]
        
        if proposed_val < limits["min"] or proposed_val > limits["max"]:
            logger.critical(f"Safety Violation: Proposed {param}={proposed_val:.2f} is outside [{limits['min']}, {limits['max']}]")
            return False
            
        return True

advisory_guard = AdvisoryGuard()
