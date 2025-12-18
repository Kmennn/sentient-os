import pytest
from brain.explainability.week_narrator import WeekNarrator
from brain.week.week_policy import WeekPolicy
from brain.week.week_plan import WeekPlan, WeeklyPattern

def test_narrator_output():
    narrator = WeekNarrator()
    plan = WeekPlan("2023-01-01")
    plan.patterns.append(WeeklyPattern("TEST", "Test Insight"))
    
    text = narrator.narrate(plan)
    assert "Test Insight" in text
    assert "Weekly Insights" in text

def test_policy_filtering():
    policy = WeekPolicy()
    
    high_conf = WeeklyPattern("TEST", "High", confidence=0.95)
    med_conf = WeeklyPattern("TEST", "Med", confidence=0.85)
    low_conf = WeeklyPattern("TEST", "Low", confidence=0.5)
    
    # Low Trust
    assert policy.should_show_insight(high_conf, 0.1) is True
    assert policy.should_show_insight(med_conf, 0.1) is False
    
    # Normal Trust
    assert policy.should_show_insight(med_conf, 0.5) is True
