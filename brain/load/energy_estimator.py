from brain.day.day_plan import DayPlan
from brain.load.load_model import LoadSnapshot, LoadLevel

class EnergyEstimator:
    """
    Estimates cognitive load based on DayPlan metrics.
    """
    
    def estimate_load(self, day_plan: DayPlan) -> LoadSnapshot:
        # Base score
        score = 0
        details = []
        
        # 1. Total Items (Routines + Tasks)
        total_items = len(day_plan.items)
        score += total_items * 10 
        
        # 2. Conflicts
        conflicts = sum(1 for item in day_plan.items if item.warnings)
        score += conflicts * 20
        if conflicts > 0:
            details.append(f"{conflicts} potential conflicts detected.")
            
        # 3. Density Check (Simplified)
        # If score > 80 -> HIGH
        # > 40 -> MED
        # else -> LOW
        
        level = LoadLevel.LOW
        density_label = "Light"
        
        if score > 80:
            level = LoadLevel.HIGH
            density_label = "Heavy"
            score = 100 # Cap
        elif score > 40:
            level = LoadLevel.MED
            density_label = "Moderate"
        else:
            density_label = "Light"
            
        return LoadSnapshot(
            date_str=day_plan.date_str,
            level=level,
            score=min(score, 100),
            density_label=density_label,
            details=details
        )
