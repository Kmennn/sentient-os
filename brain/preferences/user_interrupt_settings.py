from dataclasses import dataclass
from brain.preferences.interrupt_style import InterruptStyle

@dataclass
class UserInterruptSettings:
    user_id: str
    style: InterruptStyle = InterruptStyle.ASK_FOR_IMPORTANT
    
    # In v9, persistence logic would load this.
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "style": self.style.value
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("user_id", "user_default"),
            style=InterruptStyle(data.get("style", "ask_for_important"))
        )
