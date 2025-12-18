from typing import Tuple
from brain.context.focus_state import FocusState
from brain.context.calendar_focus_provider import CalendarFocusProvider
from brain.context.manual_focus_provider import ManualFocusProvider

class FocusResolver:
    """
    Combines signals from Calendar and Manual providers into a single authoritative FocusState.
    """
    def __init__(self, manual: ManualFocusProvider, calendar: CalendarFocusProvider):
        self.manual = manual
        self.calendar = calendar
        
    def resolve(self) -> Tuple[FocusState, str]:
        # Priority 1: Manual Focus (Overrides everything)
        manual_state = self.manual.get_state()
        if manual_state == FocusState.FOCUS_SESSION:
            return FocusState.FOCUS_SESSION, "manual"
            
        # Priority 2: Calendar Meeting
        cal_state = self.calendar.get_state()
        if cal_state == FocusState.MEETING:
            return FocusState.MEETING, "calendar"
            
        # Default
        return FocusState.FREE, "none"
