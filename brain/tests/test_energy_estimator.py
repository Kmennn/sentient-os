import pytest
from brain.load.energy_estimator import EnergyEstimator
from brain.day.day_plan import DayPlan, PlanItem
from brain.load.load_model import LoadLevel

def test_estimator_high_load():
    estimator = EnergyEstimator()
    day = DayPlan("2023-01-01")
    
    # Add 10 items (10 * 10 = 100 score)
    for i in range(10):
        day.items.append(PlanItem(str(i), "TASK", f"T{i}", 0, 3600))
        
    snapshot = estimator.estimate_load(day)
    
    assert snapshot.level == LoadLevel.HIGH
    assert snapshot.density_label == "Heavy"
    assert snapshot.score == 100

def test_estimator_conflict_penalty():
    estimator = EnergyEstimator()
    day = DayPlan("2023-01-01")
    
    # 2 items, both conflicting
    i1 = PlanItem("1", "TASK", "T1", 0, 3600)
    i1.warnings.append("Conflict")
    i2 = PlanItem("2", "TASK", "T2", 0, 3600)
    i2.warnings.append("Conflict")
    
    day.items = [i1, i2]
    
    # Score: 2 items * 10 = 20.
    # Conflicts: 2 * 20 = 40.
    # Total = 60 -> MED
    
    snapshot = estimator.estimate_load(day)
    
    assert snapshot.level == LoadLevel.MED
    assert snapshot.score >= 60
    assert len(snapshot.details) > 0
