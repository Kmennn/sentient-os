from typing import Tuple
from brain.context.presence_state import PresenceState
from brain.context.app_presence_provider import AppPresenceProvider
from brain.context.manual_presence_provider import ManualPresenceProvider

class PresenceResolver:
    """
    Aggregates presence signals. Manual > App > Default.
    """
    def __init__(self, manual: ManualPresenceProvider, app: AppPresenceProvider):
        self.manual = manual
        self.app = app
        
    def resolve(self) -> Tuple[PresenceState, str]:
        # 1. Manual Override
        manual_st = self.manual.get_state()
        if manual_st:
            return manual_st, "manual"
            
        # 2. App Heuristic
        app_st = self.app.get_state()
        if app_st != PresenceState.UNKNOWN:
            return app_st, "app_heuristic"
            
        # 3. Default
        # Conservative Default: UNKNOWN (assume cautious) or ALONE (if user prefers).
        # Let's default to ALONE for MVP usability, UNKNOWN might block too much if logic is strict.
        # But Plan says "Default -> UNKNOWN".
        return PresenceState.UNKNOWN, "default"
