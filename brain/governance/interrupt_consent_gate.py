from brain.intents.interrupt_reason import InterruptReason
from brain.memory.interrupt_memory import InterruptMemory
from brain.preferences.interrupt_preference_inferer import InterruptPreferenceInferer
from brain.preferences.interrupt_preferences import PreferenceBias
from brain.preferences.interrupt_windows import InterruptWindowMode
from brain.preferences.user_interrupt_schedule import UserInterruptSchedule
from brain.preferences.user_interrupt_settings import UserInterruptSettings
from brain.preferences.interrupt_style import InterruptStyle
from brain.governance.interrupt_time_guard import InterruptTimeGuard

from brain.context.focus_state import FocusState

class InterruptConsentGate:
    """
    Decides if a Deferred Interrupt (one that was silenced) 
    should be escalated to a Permission Request (Ask User).
    Uses Time Guard -> Explicit User Style -> Learned Preferences -> Defaults.
    """
    def __init__(self, memory: InterruptMemory = None):
        self.memory = memory or InterruptMemory() # Fallback if not injected, but should be shared instance
        self.inferer = InterruptPreferenceInferer()
        self.time_guard = InterruptTimeGuard()

    def evaluate(self, reason: InterruptReason, settings: UserInterruptSettings, schedule: UserInterruptSchedule, current_focus: FocusState = FocusState.FREE, trust_score: float = 0.5) -> bool:
        # Initial Policy: 
        # Safety -> Already Approved by Qualifier (never gets here).
        
        if not reason:
            return False
            
        # 1. TIME GUARD (New v8.2 + v8.3)
        # Checks if we are allowed to talk right now (considering Focus).
        
        time_decision = self.time_guard.evaluate(reason, schedule, current_focus)
        if time_decision == InterruptWindowMode.SILENT:
            return False
            
        # 2. Check Explicit User Style (The Boss)
        if settings.style == InterruptStyle.NEVER_INTERRUPT:
            return False
        if settings.style == InterruptStyle.ALWAYS_ASK:
            return True
            
        # 3. Check Logic for ASK_FOR_IMPORTANT (Default)
        # If Time Guard said IMPORTANT_ONLY, we already filtered trivial reasons above.
        
        # 4. Check Memory Bias (The Assistant)
        history = self.memory.get_history(reason)
        preference = self.inferer.infer(reason, history)
        
        if preference.bias == PreferenceBias.LIKELY_REJECT:
            return False
            
        # If Neutral or Accept, Ask.
        return True
