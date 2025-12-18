from dataclasses import dataclass, field
from typing import List
from brain.preferences.interrupt_windows import InterruptWindow, InterruptWindowMode

@dataclass
class UserInterruptSchedule:
    user_id: str
    timezone: str = "local"
    windows: List[InterruptWindow] = field(default_factory=list)
    
    @staticmethod
    def create_default(user_id: str) -> 'UserInterruptSchedule':
        # Default: 09:00 - 18:00 IMPORTANT_ONLY
        # Everything else falls to SILENT (handled by guard logic if no window matches)
        # Or we explicitly define the SILENT windows?
        # Let's define the ACTIVE window.
        
        w_work = InterruptWindow("09:00", "18:00", InterruptWindowMode.IMPORTANT_ONLY, "Work Hours")
        # Let's say evening is ALLOW_ALL for testing? Or just keep simple.
        # Strict request: "09:00–18:00 -> IMPORTANT_ONLY, Outside -> SILENT"
        
        return UserInterruptSchedule(user_id=user_id, windows=[w_work])

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "timezone": self.timezone,
            "windows": [w.to_dict() for w in self.windows]
        }
        
    @classmethod
    def from_dict(cls, data):
        windows = []
        if "windows" in data:
            for w_data in data["windows"]:
                windows.append(InterruptWindow.from_dict(w_data))
        return cls(
            user_id=data.get("user_id", "user_default"),
            timezone=data.get("timezone", "local"),
            windows=windows
        )
