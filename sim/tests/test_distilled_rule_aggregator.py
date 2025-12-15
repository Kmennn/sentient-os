
import pytest
from sim.rl.distilled_rule_aggregator import DistilledRuleAggregator

def test_aggregation_max():
    agg = DistilledRuleAggregator()
    inputs = [
        {"suggested_safe_height": 0.1},
        {"suggested_safe_height": 0.2},
        {"suggested_safe_height": 0.15}
    ]
    
    result = agg.aggregate(inputs)
    assert result["suggested_safe_height"] == 0.2
    assert result["aggregation_count"] == 3
