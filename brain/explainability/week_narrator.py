from brain.week.week_plan import WeekPlan

class WeekNarrator:
    """
    Generates text summaries for weekly patterns.
    """
    
    def narrate(self, plan: WeekPlan) -> str:
        if not plan.patterns:
            return "No significant patterns detected this week."
            
        lines = []
        for p in plan.patterns:
            # We could add more flavor here based on type
            lines.append(f"• {p.description}")
            
        return "Weekly Insights:\n" + "\n".join(lines)
