import pytest
from brain.simulation.what_if_engine import WhatIfEngine
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType
from brain.day.day_plan import DayPlan, PlanItem

def test_engine_move_task():
    engine = WhatIfEngine()
    day = DayPlan("2023-01-01")
    i1 = PlanItem("1", "TASK", "T1", 3600, 3600) # 1:00 - 2:00
    i2 = PlanItem("2", "TASK", "T2", 7200, 3600) # 2:00 - 3:00
    day.items = [i1, i2]
    
    # Move T1 to overlap T2 (Move to 2:30)
    scenario = WhatIfScenario("s1", ChangeType.MOVE_TASK, "1", new_start_seconds=6300) # 1:45? No 6300/3600 = 1.75 = 1:45
    # 2:30 = 2.5 * 3600 = 9000. 
    # Let's move T1 to 1:30 (5400) -> End 2:30. Overlaps T2 (Starts 2:00)
    scenario.new_start_seconds = 5400
    
    sim = engine.simulate(day, scenario)
    
    assert sim.items[0].start_seconds == 5400
    assert len(sim.items[0].warnings) > 0 # Should have overlap warning
    assert "Simulated Overlap" in sim.items[0].warnings[0]

def test_engine_remove_task():
    engine = WhatIfEngine()
    day = DayPlan("2023-01-01")
    i1 = PlanItem("1", "TASK", "T1", 3600, 3600)
    day.items = [i1]
    
    scenario = WhatIfScenario("s2", ChangeType.REMOVE_TASK, "1")
    sim = engine.simulate(day, scenario)
    
    assert len(sim.items) == 0
