import pytest
from brain.explainability.day_narrator import DayNarrator
from brain.day.day_plan import DayPlan, PlanItem

def test_narrator_summary():
    narrator = DayNarrator()
    plan = DayPlan("2023-01-01")
    
    plan.items.append(PlanItem("r1", "ROUTINE", "Focus", 32400, 3600))
    plan.items[0].warnings.append("Conflict")
    
    utils = narrator.narrate(plan)
    
    assert "Focus" in utils
    assert "Warning" in utils
    assert "overlaps" in utils or "attention" in utils
