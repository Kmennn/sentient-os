import pytest
from brain.simulation.impact_comparator import ImpactComparator
from brain.explainability.what_if_narrator import WhatIfNarrator
from brain.day.day_plan import DayPlan, PlanItem
from brain.simulation.what_if_engine import WhatIfEngine
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType

def test_impact_analysis():
    # Setup
    before = DayPlan("2023-01-01")
    # Low load item
    before.items.append(PlanItem("1", "TASK", "T1", 3600, 3600))
    
    # Simulate adding conflicts (via logic simulation or manual setup)
    # Let's manually setup 'After' for unit testing Comparator directly
    after = DayPlan("2023-01-01")
    i1 = PlanItem("1", "TASK", "T1", 3600, 3600)
    i1.warnings.append("Overlap")
    i2 = PlanItem("2", "TASK", "T2", 3600, 3600)
    i2.warnings.append("Overlap")
    after.items = [i1, i2]
    
    comparator = ImpactComparator()
    report = comparator.compare(before, after)
    
    assert report.conflict_delta == 2 # 0 -> 2
    assert report.load_score_delta > 0
    
    narrator = WhatIfNarrator()
    text = narrator.narrate(report)
    
    assert "introduces 2 new conflict" in text
    assert "increases" in text # Load increased
