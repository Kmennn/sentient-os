import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class IntentEngine:
    def __init__(self):
        self.commands = {
            r"stop": "stop_all",
            r"hush": "mute",
            r"mute": "mute",
            r"open unknown": "unknown_action"
        }
    
    def match_and_execute(self, text: str) -> Optional[str]:
        """
        Matches text against local commands and returns the action ID if matched.
        Executing the action would typically happen in ActionExecutor.
        """
        text = text.lower().strip()
        for pattern, action in self.commands.items():
            if re.search(pattern, text):
                logger.info(f"Local Intent Matched: {text} -> {action}")
                return action
        return None

