
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AdvisorySuggestion:
    parameter: str
    delta: float
    reason: str
    source_policy: str
    confidence: float

class PolicyAdvisor:
    """
    Generates advisory suggestions based on distilled policy rules.
    """
    def __init__(self):
        self.active_policy_id = "sim_v3.1_default"
        self.distilled_rules: Dict[str, float] = {}

    def load_rules(self, rules: Dict[str, float]):
        self.distilled_rules = rules
        logger.info(f"Advisor loaded rules: {rules}")

    def get_suggestion(self, task_context: str) -> Optional[AdvisorySuggestion]:
        """
        Returns a suggestion if context matches a rule.
        """
        # Example: If task="pick_place_cluttered" and we have safe_height rule
        if "cluttered" in task_context and "suggested_safe_height" in self.distilled_rules:
            safe_h = self.distilled_rules["suggested_safe_height"]
            
            # Suggest increasing lift height to Sim's safe recommendation
            current_default = 0.05
            delta = safe_h - current_default
            
            if delta > 0.01:
                return AdvisorySuggestion(
                    parameter="lift_height",
                    delta=delta,
                    reason=f"Simulation found clutter requires {safe_h:.2f}m clearance.",
                    source_policy=self.active_policy_id,
                    confidence=0.85
                )
                
        return None

policy_advisor = PolicyAdvisor()
