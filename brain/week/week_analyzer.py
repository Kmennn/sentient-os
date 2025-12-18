from typing import List
from brain.week.week_plan import WeekPlan, WeeklyPattern
from brain.day.day_plan import DayPlan

class WeekAnalyzer:
    """
    Analyzes multiple DayPlans to detect patterns.
    """
    
    def analyze_week(self, days: List[DayPlan]) -> WeekPlan:
        if not days:
            return WeekPlan(week_start_date="Unknown")
            
        start_date = days[0].date_str
        plan = WeekPlan(week_start_date=start_date, days=days)
        
        # Detect Patterns
        # 1. Conflict Prone Days
        for i, day in enumerate(days):
            conflict_count = sum(1 for item in day.items if item.warnings)
            if conflict_count >= 2: # Threshold for "Conflict Prone"
                # Map index to weekday? Need date parsing or assume contiguous
                # We'll stick to generic description for now unless we parse date.
                pattern = WeeklyPattern(
                    type="CONFLICT_PRONE",
                    description=f"Day {i+1} ({day.date_str}) has multiple conflicts.",
                    confidence=0.9
                )
                plan.patterns.append(pattern)
                
        # 2. Routine Density
        total_routines = sum(sum(1 for item in day.items if item.type == 'ROUTINE') for day in days)
        if total_routines > 10:
             plan.patterns.append(WeeklyPattern(
                 type="ROUTINE_HEAVY",
                 description="This week is heavily structured with routines.",
                 confidence=0.8
             ))
             
        return plan
