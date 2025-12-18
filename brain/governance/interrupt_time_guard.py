from brain.intents.interrupt_reason import InterruptReason
from brain.preferences.interrupt_windows import InterruptWindow, InterruptWindowMode
from brain.preferences.user_interrupt_schedule import UserInterruptSchedule
from brain.context.focus_state import FocusState

class InterruptTimeGuard:
    """
    Determines if an interrupt is allowed at the current time based on the schedule,
    overridden by Focus Context (Meetings/Deep Work).
    """
    
    def evaluate(self, reason: InterruptReason, schedule: UserInterruptSchedule, current_focus: FocusState = FocusState.FREE) -> InterruptWindowMode:
        
        # 1. Check Contextual Overrides (Focus/Meeting)
        if current_focus in [FocusState.FOCUS_SESSION, FocusState.MEETING]:
            # Implicitly SILENT, regardless of schedule.
            return InterruptWindowMode.SILENT

        # 2. Get current time "HH:MM"
        # In real app, use timezone. For MVP, use local system time.
        now_struct = time.localtime()
        now_str = f"{now_struct.tm_hour:02d}:{now_struct.tm_min:02d}"
        
        current_mode = InterruptWindowMode.SILENT # Default if no window matches
        
        for window in schedule.windows:
            if window.contains_time(now_str):
                current_mode = window.mode
                break
                
        # Now check Reason against Mode
        if current_mode == InterruptWindowMode.SILENT:
            return InterruptWindowMode.SILENT # Gate will block (unless safety)
            
        if current_mode == InterruptWindowMode.IMPORTANT_ONLY:
            if reason in [InterruptReason.DEADLINE_RISK, InterruptReason.USER_DEPENDENCY]:
                return InterruptWindowMode.IMPORTANT_ONLY # Allowed
            else:
                return InterruptWindowMode.SILENT # Block optimization/others
                
        # ALLOW_ALL
        return InterruptWindowMode.ALLOW_ALL
