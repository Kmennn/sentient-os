import re
from typing import Optional

class IntentParser:
    """
    Compiles natural language into strict system commands.
    Deterministic, rule-based, safe.
    """
    
    def compile(self, text: str) -> Optional[str]:
        text = text.strip().lower()
        if not text:
            return None
            
        # 1. Pass-through strictly formatted commands
        if text.startswith("/"):
            return text
            
        # 2. Focus Intent
        # "focus for 30 mins", "start focus", "deep work"
        if "focus" in text or "deep work" in text:
            # Check for stop
            if "stop" in text or "cancel" in text or "end" in text:
                return "/focus stop"
            
            # Extract duration
            # "30 min", "1 hour", "45m"
            duration = 25 # Default
            
            # Regex for "X mins"
            match_min = re.search(r'(\d+)\s*(m|min|minute)', text)
            if match_min:
                duration = int(match_min.group(1))
            
            # Regex for "X hours"
            match_hour = re.search(r'(\d+)\s*(h|hr|hour)', text)
            if match_hour:
                duration = int(match_hour.group(1)) * 60
                
            return f"/focus {duration}"

        # 3. Status Intent
        # "status", "health", "how are you", "system check"
        if any(x in text for x in ["status", "system check", "how are you", "health"]):
            return "/status"
            
        # 4. Stop/Preempt/Cancel Intent (General)
        # "stop", "halt", "abort"
        if text in ["stop", "halt", "abort", "stop everything"]:
            return "/stop"
            
        # 5. Mission Intent (Explicit)
        # "new mission: ...", "task: ..."
        # Only if explicit colon usage or "start mission" keywords to avoid false positives
        if text.startswith("mission:") or text.startswith("task:"):
            return f"/mission {text.split(':', 1)[1].strip()}"
            
        # 6. Action Macros (H8)
        # "clean system"
        if "clean system" in text or "cleanup" in text:
            return "/macro clean_system"
            
        # "prepare for meeting"
        if "meeting" in text and ("prep" in text or "prepare" in text):
            return "/macro meeting_prep"
            
        # "wrap up work"
        if "wrap up" in text:
            return "/macro wrap_up"

        # Ambiguous / Unknown
        return None
