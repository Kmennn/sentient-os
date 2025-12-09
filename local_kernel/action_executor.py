
import logging
import pyautogui
import subprocess
import time
import os

logger = logging.getLogger("action_executor")

# Security Configuration
ALLOW_REAL_ACTIONS = False # Default to SAFE

class ActionExecutor:
    def __init__(self):
        # Fail-safe: moving mouse to corner will throw exception
        pyautogui.FAILSAFE = True
        self._last_action_time = 0.0
        self._min_interval = 0.5 # Max 2 actions/sec
        
        # Deduplication History (timestamp, action, params)
        self._action_history = [] 
        self._dedupe_window = 0.5 # Ignore duplicates within 500ms
        
        # Intent Map
        self._intent_map = {
            "scroll slowly": ("SCROLL_DOWN", 100),
            "scroll fast": ("SCROLL_DOWN", 1000),
            "scroll up slowly": ("SCROLL_UP", 100),
            "scroll up fast": ("SCROLL_UP", 1000),
            "open chrome": ("OPEN_APP", "chrome"),
            "open browser": ("OPEN_APP", "browser"),
            "close window": ("HOTKEY", "alt,f4"),
            "copy": ("HOTKEY", "ctrl,c"),
            "paste": ("HOTKEY", "ctrl,v"),
        }

    def set_security_mode(self, allow_real: bool):
        global ALLOW_REAL_ACTIONS
        ALLOW_REAL_ACTIONS = allow_real
        logger.info(f"Security Mode Update: Real Actions Allowed = {ALLOW_REAL_ACTIONS}")

    def _resolve_intent(self, action_type: str, params: any):
        """Map natural language intents to internal actions."""
        key = action_type.lower().strip()
        if key in self._intent_map:
            return self._intent_map[key]
            
        # Fallback for standard actions
        return action_type.upper(), params

    def execute(self, action_type: str, params: any, mode: str = "SIMULATED") -> dict:
        """
        Executes or Simulates an action.
        """
        global ALLOW_REAL_ACTIONS
        
        # 1. Resolve Intent
        resolved_action, resolved_params = self._resolve_intent(action_type, params)
        
        # 2. Deduplication
        now = time.time()
        # Clean old history
        self._action_history = [a for a in self._action_history if now - a[0] < 2.0]
        
        # Check for recent duplicate
        key = (resolved_action, str(resolved_params))
        for ts, act, p in self._action_history:
            if act == resolved_action and str(p) == str(resolved_params):
                if now - ts < self._dedupe_window:
                    logger.warning(f"Duplicate action suppressed: {resolved_action}")
                    return {"status": "ignored", "reason": "Duplicate action detected"}
        
        # Add to history
        self._action_history.append((now, resolved_action, resolved_params))

        # 3. Rate Limiting (Global)
        if now - self._last_action_time < self._min_interval:
            wait = self._min_interval - (now - self._last_action_time)
            time.sleep(wait)
        self._last_action_time = time.time()

        should_execute = False
        if mode == "REAL":
            if ALLOW_REAL_ACTIONS:
                should_execute = True
            else:
                return {"status": "denied", "reason": "Global Safety Lock is ON"}
        
        logger.info(f"Processing Action: {resolved_action} Params: {resolved_params} Mode: {mode}")

        if not should_execute:
            return {"status": "simulated", "action": resolved_action, "detail": "Action handled in simulation mode."}

        # REAL EXECUTION
        try:
            if resolved_action == "OPEN_APP":
                app_name = resolved_params
                if app_name.lower() in ["notepad", "calc", "calculator"]:
                     cmd = "notepad.exe" if "notepad" in app_name.lower() else "calc.exe"
                     subprocess.Popen(cmd)
                     return {"status": "success", "detail": f"Opened {cmd}"}
                
                if app_name.lower() in ["chrome", "browser", "edge"]:
                     import webbrowser
                     webbrowser.open("https://google.com")
                     return {"status": "success", "detail": "Opened default browser"}

                return {"status": "failed", "reason": f"App '{app_name}' not in whitelist"}

            elif resolved_action == "TYPE_TEXT":
                text = resolved_params
                pyautogui.write(text, interval=0.05)
                return {"status": "success", "detail": f"Typed {len(text)} chars"}
                
            elif resolved_action == "MOUSE_MOVE":
                x = int(resolved_params.get("x", 0))
                y = int(resolved_params.get("y", 0))
                
                screen_w, screen_h = pyautogui.size()
                if not (0 <= x <= screen_w and 0 <= y <= screen_h):
                    return {"status": "failed", "reason": f"Coordinates {x},{y} out of bounds"}

                pyautogui.moveTo(x, y, duration=0.5)
                return {"status": "success", "detail": f"Moved to {x},{y}"}

            elif resolved_action == "CLICK":
                pyautogui.click()
                return {"status": "success", "detail": "Clicked"}
            
            elif resolved_action == "HOTKEY":
                keys = resolved_params.split(",")
                pyautogui.hotkey(*keys)
                return {"status": "success", "detail": f"Sent hotkey {resolved_params}"}

            elif "SCROLL" in resolved_action:
                amount = int(resolved_params) if isinstance(resolved_params, (int, float)) else 500
                if "UP" in resolved_action:
                    pyautogui.scroll(abs(amount))
                else:
                    pyautogui.scroll(-abs(amount))
                return {"status": "success", "detail": f"Scrolled {amount}"}

            else:
                return {"status": "error", "reason": f"Unknown action: {resolved_action}"}

        except Exception as e:
            logger.error(f"Execution Error: {e}")
            return {"status": "error", "reason": str(e)}

action_executor = ActionExecutor()
