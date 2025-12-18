import pytest
from brain.week.week_analyzer import WeekAnalyzer
from brain.week.week_plan import WeekPlan
from brain.day.day_plan import DayPlan, PlanItem

def test_analyzer_detects_conflicts():
    analyzer = WeekAnalyzer()
    
    # Create a day with conflicts
    d1 = DayPlan("2023-01-01")
    i1 = PlanItem("1", "TASK", "Task1", 0, 3600)
    i1.warnings.append("Overlap")
    i2 = PlanItem("2", "TASK", "Task2", 0, 3600)
    i2.warnings.append("Overlap")
    
    d1.items = [i1, i2]
    
    wk = analyzer.analyze_week([d1])
    
    assert len(wk.patterns) > 0
    assert wk.patterns[0].type == "CONFLICT_PRONE"
    assert "Day 1" in wk.patterns[0].description

def test_analyzer_detects_routine_heavy():
    analyzer = WeekAnalyzer()
    days = []
    for i in range(7):
        d = DayPlan(f"2023-01-0{i+1}")
        # Add 2 routines per day = 14 total
        d.items.append(PlanItem("r1", "ROUTINE", "R1", 0, 3600))
        d.items.append(PlanItem("r2", "ROUTINE", "R2", 0, 3600))
        days.append(d)
        
    wk = analyzer.analyze_week(days)
    
    heavy = next((p for p in wk.patterns if p.type == "ROUTINE_HEAVY"), None)
    assert heavy is not None
