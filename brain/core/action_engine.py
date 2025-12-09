from typing import Dict, Any

class ActionEngine:
    def execute_intent(self, intent: str) -> Dict[str, Any]:
        """
        Maps an intent to a safe mock action payload.
        """
        intent = intent.lower()
        
        if "setting" in intent:
            return {"status": "simulated", "action": "open_settings", "target": "settings_app"}
        
        if "scroll" in intent:
            direction = "up" if "up" in intent else "down"
            return {"status": "simulated", "action": "scroll", "direction": direction}
            
        if "click" in intent:
             return {"status": "simulated", "action": "click", "target": "center_screen"}

        return {"status": "unknown", "action": "none", "reason": "No mapping for intent"}

action_engine = ActionEngine()
