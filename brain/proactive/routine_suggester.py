import time
import datetime
from typing import List, Optional
from brain.routines.routine import Routine
from brain.proactive.suggestion_guard import SuggestionGuard

class RoutineSuggester:
    """
    Checks upcoming routines and triggers proactive suggestions.
    """
    
    def __init__(self, guard: SuggestionGuard):
        self.guard = guard
        
    def check_suggestions(self, current_time: float, routines: List[Routine]) -> Optional[Routine]:
        """
        Returns the Routine to suggest, if any.
        Look ahead 15 mins (900s).
        """
        now_dt = datetime.datetime.fromtimestamp(current_time)
        seconds_midnight = now_dt.hour * 3600 + now_dt.minute * 60 + now_dt.second
        
        # Target time = Now + 15 mins
        target_time = seconds_midnight + 900
        
        for r in routines:
            # If routine starts around target_time (tolerance 5 mins)
            # e.g. Routine starts at 9:00 (32400). Now is 8:45 (31500). Target 9:00.
            if abs(r.time_of_day_seconds - target_time) < 300:
                # Found approaching routine
                if self.guard.check_guard(r.routine_id, current_time):
                    # Suggest it!
                    # Mark guard immediately? Or wait for emit?
                    # Ideally mark as "Suggested" to prevent double trigger in next tick
                    self.guard.record_suggestion(r.routine_id, current_time)
                    return r
                    
        return None
