from brain.day.day_planner import DayPlanner
from brain.week.week_analyzer import WeekAnalyzer
from brain.week.week_plan import WeekPlan
from brain.load.energy_estimator import EnergyEstimator
from brain.load.load_model import LoadSnapshot
from brain.routines.routine_approval import RoutineApproval
import datetime
from typing import List

class SchedulerService:
    def __init__(self):
        self.day_planner = DayPlanner()
        self.week_analyzer = WeekAnalyzer()
        self.energy_estimator = EnergyEstimator()
        self.routine_approval = RoutineApproval()

    def get_protected_routines(self):
        return list(self.routine_approval.get_protected_routines())

    def get_day_snapshot(self, queued_missions) -> 'DayPlan':
        routines = self.get_protected_routines()
        queued = list(queued_missions)
        return self.day_planner.generate_plan(routines, queued, [], datetime.date.today())

    def get_week_snapshot(self, queued_missions) -> WeekPlan:
        days = []
        today = datetime.date.today()
        routines = self.get_protected_routines()
        queued = list(queued_missions)
        
        for i in range(7):
            date = today + datetime.timedelta(days=i)
            day_plan = self.day_planner.generate_plan(routines, queued, [], date)
            days.append(day_plan)
            
        return self.week_analyzer.analyze_week(days)

    def get_load_snapshot(self, queued_missions) -> List[LoadSnapshot]:
        snapshots = []
        today = datetime.date.today()
        routines = self.get_protected_routines()
        queued = list(queued_missions)
        
        for i in range(7):
            date = today + datetime.timedelta(days=i)
            day_plan = self.day_planner.generate_plan(routines, queued, [], date)
            snap = self.energy_estimator.estimate_load(day_plan)
            snapshots.append(snap)
            
        return snapshots
