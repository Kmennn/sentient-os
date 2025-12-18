from typing import List, Dict, Any
from brain.routines.routine import Routine
import statistics

class RoutineDetector:
    """
    Detects patterns in mission history to suggest Routines.
    """
    
    def detect_candidates(self, history: List[Dict[str, Any]]) -> List[Routine]:
        """
        History is a list of completed mission dicts (start_time, name/type, etc.)
        Basic algo: Group by name. If count >= 3 and times are similar (std dev low), candidate.
        """
        candidates = []
        
        # Group by name/description
        groups = {}
        for item in history:
            key = item.get("name") or item.get("description")
            if not key: continue
            if key not in groups: groups[key] = []
            groups[key].append(item)
            
        for name, items in groups.items():
            if len(items) < 3:
                continue
                
            # Analyze start times (seconds from midnight)
            # Need to convert timestamp to time_of_day since midnight per item
            # For simplicity, assume item["start_time_of_day"] is available or calculated
            # In real system, we'd parse timestamp. Here we assume pre-processed or mock.
            
            times = [x.get("start_time_of_day", 0) for x in items]
            
            # If times are clustered (e.g. std dev < 1 hour)
            if len(times) > 1:
                stdev = statistics.stdev(times)
                if stdev < 3600: # 1 hour tolerance
                    avg_time = int(statistics.mean(times))
                    avg_dur = int(statistics.mean([x.get("duration", 0) for x in items]))
                    
                    # Create candidate
                    r = Routine(
                        name=name,
                        time_of_day_seconds=avg_time,
                        duration_seconds=avg_dur,
                        days_of_week=[0,1,2,3,4,5,6], # Assume daily for MVP or scan dates
                        confidence=0.8
                    )
                    candidates.append(r)
                    
        return candidates
