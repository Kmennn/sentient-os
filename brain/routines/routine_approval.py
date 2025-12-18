from typing import List, Dict
from brain.routines.routine import Routine

class RoutineApproval:
    """
    Manages the lifecycle of Routines (Candidate -> Protected -> Ignored).
    """
    
    def __init__(self):
        self.candidates: Dict[str, Routine] = {}
        self.protected: Dict[str, Routine] = {}
        self.ignored_ids: List[str] = []
        
    def add_candidate(self, routine: Routine):
        if routine.routine_id not in self.protected and routine.routine_id not in self.ignored_ids:
            self.candidates[routine.routine_id] = routine
            
    def protect_routine(self, routine_id: str):
        if routine_id in self.candidates:
            r = self.candidates.pop(routine_id)
            r.protected = True
            self.protected[routine_id] = r
    
    def ignore_routine(self, routine_id: str):
        if routine_id in self.candidates:
            self.candidates.pop(routine_id)
            self.ignored_ids.append(routine_id)
            
    def get_protected_routines(self) -> List[Routine]:
        return list(self.protected.values())
