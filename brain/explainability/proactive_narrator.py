from brain.routines.routine import Routine

class ProactiveNarrator:
    """
    Generates text for proactive suggestions.
    """
    
    def explain_suggestion(self, routine: Routine, style: str = 'NORMAL') -> str:
        start_fmt = f"{routine.time_of_day_seconds / 3600:.0f}:{(routine.time_of_day_seconds % 3600) / 60:02.0f}"
        
        if style == 'ASSERTIVE':
            return f"Heads up! '{routine.name}' starts soon. Do you need to prepare?"
        elif style == 'PASSIVE':
             return f"Upcoming: '{routine.name}'. Assistance available if needed."
             
        return f"It's almost time for '{routine.name}'. Would you like me to set up?"
