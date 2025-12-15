
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PhysicalFailureExplainer:
    """
    Translates error codes to human-readable explanations.
    """
    def explain(self, error_type: str, context: dict) -> str:
        
        if error_type == "OCCLUSION":
            return f"Path blocked by obstacle near ({context.get('x',0):.2f}, {context.get('y',0):.2f})."
            
        if error_type == "AFFORDANCE_VIOLATION":
            return f"Action '{context.get('action')}' is not allowed on object '{context.get('object_label')}'."
            
        if error_type == "VERIFICATION_FAILED":
            return f"Step verification failed: {context.get('details', 'Unknown')}."
            
        if error_type == "GUARD_BLOCK":
             return "Safety Guard prevented unsafe movement."
             
        return f"Unknown error: {error_type}"

physical_failure_explainer = PhysicalFailureExplainer()
