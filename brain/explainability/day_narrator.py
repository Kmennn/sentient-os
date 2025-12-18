from typing import List
from brain.day.day_plan import DayPlan

class DayNarrator:
    """
    Generates natural language summaries for the Day Plan.
    """
    
    def narrate(self, plan: DayPlan) -> str:
        """
        Returns a short summary of the day.
        """
        if not plan.items:
            return "Your day looks clear."
            
        routines = [i for i in plan.items if i.type == 'ROUTINE']
        tasks = [i for i in plan.items if i.type == 'TASK']
        conflicts = [i for i in plan.items if i.warnings]
        
        parts = []
        
        # Morning/Afternoon breakdown? 
        # For simplicity, just count.
        if routines:
            names = ", ".join([r.name for r in routines])
            parts.append(f"You have {len(routines)} protected routines: {names}.")
            
        if tasks:
            parts.append(f"There are {len(tasks)} scheduled tasks.")
            
        if conflicts:
            parts.append(f"⚠️ Warning: Detected {len(conflicts)} overlaps that may require attention.")
        else:
            parts.append("No conflicts detected.")
            
        return " ".join(parts)
