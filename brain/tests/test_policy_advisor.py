
import pytest
from brain.learning.policy_advisor import PolicyAdvisor

def test_suggestion_generation():
    advisor = PolicyAdvisor()
    advisor.load_rules({"suggested_safe_height": 0.2}) # 20cm
    
    suggestion = advisor.get_suggestion("pick_place_cluttered")
    
    assert suggestion is not None
    assert suggestion.parameter == "lift_height"
    assert suggestion.delta > 0.1 # 0.2 - 0.05 = 0.15
    assert "Simulation found" in suggestion.reason

def test_no_relevant_rule():
    advisor = PolicyAdvisor()
    advisor.load_rules({})
    
    suggestion = advisor.get_suggestion("pick_place_cluttered")
    assert suggestion is None
