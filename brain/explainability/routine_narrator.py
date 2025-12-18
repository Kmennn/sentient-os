from brain.routines.routine import Routine

class RoutineNarrator:
    """
    Explains routine-related events.
    """
    
    def explain_routine_conflict(self, intent_name: str, routine: Routine) -> str:
        return f"Mission '{intent_name}' deferred. The time slot is reserved for your protected routine: '{routine.name}'."
        
    def explain_candidate(self, routine: Routine) -> str:
        conf_pct = int(routine.confidence * 100)
        return f"Detected potential routine '{routine.name}' ({conf_pct}% confidence). Protect it?"
