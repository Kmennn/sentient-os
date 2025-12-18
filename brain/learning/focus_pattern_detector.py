import time
import uuid
from typing import List, Dict
from brain.learning.focus_pattern import FocusPattern, FocusPatternStatus

class FocusPatternDetector:
    """
    Detects recurring focus sessions.
    Simple Heuristic: if X sessions start within +/- 30 mins window.
    """
    def __init__(self):
        self.patterns: Dict[str, FocusPattern] = {}
        
    def record_session(self, start_epoch: float, duration_minutes: int):
        # Convert epoch to "HH:MM" and Weekday
        struct = time.localtime(start_epoch)
        start_min_of_day = struct.tm_hour * 60 + struct.tm_min
        weekday = struct.tm_wday
        
        # Check matching patterns
        matched = False
        for p in self.patterns.values():
            if p.status == FocusPatternStatus.REJECTED:
                continue
                
            # Check overlap/proximity
            p_start_min = self._to_mins(p.start_time)
            if abs(p_start_min - start_min_of_day) <= 30: # 30 min tolerance
                 # Match!
                 matched = True
                 p.occurrence_count += 1
                 if weekday not in p.days:
                     p.days.append(weekday)
                 
                 # Basic Confidence Growth
                 p.confidence = min(0.9, p.occurrence_count * 0.3)
                 
                 if p.confidence >= 0.7 and p.status == FocusPatternStatus.CANDIDATE:
                     p.status = FocusPatternStatus.PROPOSED
                 break
        
        if not matched:
            # Create new Candidate
            start_str = f"{struct.tm_hour:02d}:{struct.tm_min:02d}"
            end_epoch = start_epoch + (duration_minutes * 60)
            end_struct = time.localtime(end_epoch)
            end_str = f"{end_struct.tm_hour:02d}:{end_struct.tm_min:02d}"
            
            new_id = str(uuid.uuid4())[:8]
            pat = FocusPattern(
                pattern_id=new_id,
                start_time=start_str,
                end_time=end_str,
                days=[weekday],
                confidence=0.3, # Start low
                status=FocusPatternStatus.CANDIDATE
            )
            self.patterns[new_id] = pat

    def get_proposals(self) -> List[FocusPattern]:
        return [p for p in self.patterns.values() if p.status == FocusPatternStatus.PROPOSED]
        
    def _to_mins(self, t_str: str) -> int:
        h, m = map(int, t_str.split(':'))
        return h * 60 + m
