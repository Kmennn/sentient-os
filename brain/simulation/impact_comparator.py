from dataclasses import dataclass
from brain.day.day_plan import DayPlan
from brain.load.energy_estimator import EnergyEstimator
from brain.load.load_model import LoadSnapshot, LoadLevel

@dataclass
class ImpactReport:
    conflict_delta: int
    load_score_delta: int
    level_before: LoadLevel
    level_after: LoadLevel
    score_before: int
    score_after: int

class ImpactComparator:
    """
    Compares two DayPlans to quantify the impact of a change.
    """
    def __init__(self):
        self.estimator = EnergyEstimator()
        
    def compare(self, before: DayPlan, after: DayPlan) -> ImpactReport:
        snap_before = self.estimator.estimate_load(before)
        snap_after = self.estimator.estimate_load(after)
        
        # Conflict delta
        conflicts_before = sum(1 for i in before.items if i.warnings)
        conflicts_after = sum(1 for i in after.items if i.warnings)
        
        return ImpactReport(
            conflict_delta=conflicts_after - conflicts_before,
            load_score_delta=snap_after.score - snap_before.score,
            level_before=snap_before.level,
            level_after=snap_after.level,
            score_before=snap_before.score,
            score_after=snap_after.score
        )
