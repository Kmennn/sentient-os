from enum import Enum, auto
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance

class UserAction(Enum):
    ACCEPTED_DELAY = auto()
    CANCELLED_DELAY = auto()
    MANUAL_OVERRIDE = auto()

class PreferenceLearner:
    """
    Adjusts user preferences based on observed behavior.
    """
    
    def update(self, prefs: SchedulingPreferences, action: UserAction) -> bool:
        """
        Updates prefs in-place. Returns True if changed.
        """
        changed = False
        
        if action == UserAction.CANCELLED_DELAY:
            # User hated waiting. Decrease tolerance.
            if prefs.delay_tolerance == DelayTolerance.HIGH:
                prefs.delay_tolerance = DelayTolerance.MEDIUM
                changed = True
            elif prefs.delay_tolerance == DelayTolerance.MEDIUM:
                prefs.delay_tolerance = DelayTolerance.LOW
                changed = True
                
        elif action == UserAction.ACCEPTED_DELAY:
            # User accepted waiting. Maybe increase?
            # Conservative: Don't auto-increase to HIGH easily.
            # Only increase LOW -> MED if consistent?
            # For MVP, let's keep it simple: No auto-increase, only decrease on negative signal.
            pass
            
        return changed
