from brain.learning.focus_pattern import FocusPatternStatus
from brain.learning.focus_pattern_detector import FocusPatternDetector
from brain.preferences.user_interrupt_schedule import UserInterruptSchedule
from brain.preferences.interrupt_windows import InterruptWindow, InterruptWindowMode

class FocusPatternConsent:
    """
    Manages user approval of discovered patterns.
    """
    def __init__(self, detector: FocusPatternDetector):
        self.detector = detector
        
    def approve(self, pattern_id: str, schedule: UserInterruptSchedule) -> bool:
        if pattern_id in self.detector.patterns:
            p = self.detector.patterns[pattern_id]
            p.status = FocusPatternStatus.APPROVED
            
            # Create Window
            w = InterruptWindow(
                start_time=p.start_time,
                end_time=p.end_time,
                mode=InterruptWindowMode.SILENT,
                name=f"Learned Focus ({p.start_time})"
            )
            schedule.windows.append(w)
            return True
        return False
        
    def reject(self, pattern_id: str) -> bool:
        if pattern_id in self.detector.patterns:
            p = self.detector.patterns[pattern_id]
            p.status = FocusPatternStatus.REJECTED
            return True
        return False
