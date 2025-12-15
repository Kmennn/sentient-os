
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DistilledRuleAggregator:
    """
    Combines rules from multiple runs/policies.
    """
    def aggregate(self, rule_sets: List[Dict[str, float]]) -> Dict[str, float]:
        if not rule_sets:
            return {}
            
        # Example: Aggregate 'suggested_safe_height'
        heights = [r.get("suggested_safe_height", 0.0) for r in rule_sets]
        
        # We take the MAXIMUM safe height (conservative)
        safe_height = max(heights)
        
        aggregated = {
            "suggested_safe_height": safe_height,
            "aggregation_count": len(rule_sets)
        }
        
        logger.info(f"Aggregated Rules: {aggregated}")
        return aggregated

rule_aggregator = DistilledRuleAggregator()
