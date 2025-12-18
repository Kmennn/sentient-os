from dataclasses import dataclass
from typing import List, Optional
from brain.intents.intent import Intent

@dataclass
class ConflictReport:
    new_intent: Intent
    active_intent: Intent
    reason: str
    resources_involved: List[str]

class ConflictDetector:
    """
    Analyzes a new intent against a list of active intents to find potential conflicts.
    """
    
    def check_conflicts(self, new_intent: Intent, active_intents: List[Intent]) -> List[ConflictReport]:
        conflicts = []
        
        for active in active_intents:
            # 1. Resource Contention
            common_resources = list(set(new_intent.resources) & set(active.resources))
            if common_resources:
                conflicts.append(ConflictReport(
                    new_intent=new_intent,
                    active_intent=active,
                    reason="Resource Contention",
                    resources_involved=common_resources
                ))
                continue # If confirmed conflict, move to next active intent (or just report implementation choice)
                
            # 2. Time Overlap (if both have windows)
            if new_intent.time_window and active.time_window:
                if self._time_overlaps(new_intent.time_window, active.time_window):
                    conflicts.append(ConflictReport(
                        new_intent=new_intent,
                        active_intent=active,
                        reason="Time Schedule Overlap",
                        resources_involved=[]
                    ))
                    
        return conflicts

    def _time_overlaps(self, w1, w2) -> bool:
        start1, end1 = w1
        start2, end2 = w2
        return max(start1, start2) < min(end1, end2)
