from typing import Dict

class SafetyLayer:
    def validate_message(self, text: str) -> bool:
        """
        Basic safety checks.
        Returns True if safe, False otherwise.
        """
        if not text:
            return False
        if len(text) > 4096: # Prevent huge payloads
            return False
        
        # Placeholder triggers
        unsafe_keywords = ["<script>", "drop table", "rm -rf"]
        if any(k in text.lower() for k in unsafe_keywords):
            return False
            
        return True

    def classify_intent(self, text: str) -> str:
        """
        Stub for intent classification.
        """
        text = text.lower()
        
        # Vision Triggers
        if any(x in text for x in ["screen", "look at", "see", "window", "analyze"]):
            return "visual_query"
            
        if any(x in text for x in ["hi", "hello", "hey"]):
            return "smalltalk"
            
        if any(x in text for x in ["open", "run", "start", "scroll", "click"]):
            return "action"
            
        return "query"

safety_layer = SafetyLayer()
