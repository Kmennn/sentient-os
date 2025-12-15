
import logging
from typing import List, Dict, Set
from brain.vision.object_semantics import SemanticObject

logger = logging.getLogger(__name__)

class AffordanceEngine:
    """
    Determines what actions are valid for a given object.
    """
    def __init__(self):
        # Default rules
        self.rules: Dict[str, Set[str]] = {
            "vessel": {"grasp", "pour_into", "place"},
            "electronics": {"avoid"}, # No touch
            "tool": {"grasp", "use"},
            "surface": {"place_on"},
        }
        
    def get_affordances(self, obj: SemanticObject) -> Set[str]:
        # 1. Class-based lookup
        base_affordances = self.rules.get(obj.class_type, set())
        
        # 2. Property-based modification
        final_affordances = base_affordances.copy()
        
        if obj.properties.is_fragile:
            final_affordances.discard("toss") # Example
            
        if obj.properties.is_heavy:
            final_affordances.discard("lift_fast")
            
        return final_affordances

    def is_action_allowed(self, obj: SemanticObject, action: str) -> bool:
        allowed = self.get_affordances(obj)
        if action in allowed:
            return True
        logger.warning(f"Action '{action}' NOT allowed on '{obj.label}' ({obj.class_type})")
        return False

affordance_engine = AffordanceEngine()
