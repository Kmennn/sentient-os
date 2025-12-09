
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

    def set_security_mode(self, allow_real: bool):
        global ALLOW_REAL_ACTIONS
        ALLOW_REAL_ACTIONS = allow_real
        logger.info(f"Security Mode Update: Real Actions Allowed = {ALLOW_REAL_ACTIONS}")

    def execute(self, action_type: str, params: any, mode: str = "SIMULATED") -> dict:
        """
        Executes or Simulates an action.
        mode can be 'REAL' or 'SIMULATED'.
        """
        # Global override
        global ALLOW_REAL_ACTIONS
        
        # Rate Limiter
        now = time.time()
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
        
        logger.info(f"Processing Action: {action_type} Params: {params} Mode: {mode} Executing: {should_execute}")

        if not should_execute:
            # Simulation Only
            return {"status": "simulated", "action": action_type, "detail": "Action handled in simulation mode."}

        # REAL EXECUTION
        try:
            if action_type == "OPEN_APP" or action_type == "open_app":
                app_name = params
                # Simple unsafe implementation for demo (v1.8)
                if app_name.lower() in ["notepad", "calc", "calculator"]:
                     cmd = "notepad.exe" if "notepad" in app_name.lower() else "calc.exe"
                     subprocess.Popen(cmd)
                     return {"status": "success", "detail": f"Opened {cmd}"}
                
                # Browser Check
                if app_name.lower() in ["chrome", "browser", "edge"]:
                     # Try opening url
                     import webbrowser
                     webbrowser.open("https://google.com")
                     return {"status": "success", "detail": "Opened default browser"}

                return {"status": "failed", "reason": f"App '{app_name}' not in whitelist"}

            elif action_type == "TYPE_TEXT":
                text = params
                pyautogui.write(text, interval=0.05)
                return {"status": "success", "detail": f"Typed {len(text)} chars"}
                
            elif action_type == "MOUSE_MOVE":
                x = int(params.get("x", 0))
                y = int(params.get("y", 0))
                
                # Safety Bounds
                screen_w, screen_h = pyautogui.size()
                if not (0 <= x <= screen_w and 0 <= y <= screen_h):
                    return {"status": "failed", "reason": f"Coordinates {x},{y} out of bounds ({screen_w}x{screen_h})"}

                pyautogui.moveTo(x, y, duration=0.5)
                return {"status": "success", "detail": f"Moved to {x},{y}"}

            elif action_type == "CLICK":
                pyautogui.click()
                return {"status": "success", "detail": "Clicked"}

            elif "SCROLL" in action_type.upper():
                amount = int(params) if isinstance(params, (int, float)) else 500
                if "UP" in action_type.upper():
                    pyautogui.scroll(abs(amount))
                else:
                    pyautogui.scroll(-abs(amount))
                return {"status": "success", "detail": f"Scrolled {amount}"}

            else:
                return {"status": "error", "reason": f"Unknown action: {action_type}"}

        except Exception as e:
            logger.error(f"Execution Error: {e}")
            return {"status": "error", "reason": str(e)}

action_executor = ActionExecutor()
