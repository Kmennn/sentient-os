
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

    def set_security_mode(self, allow_real: bool):
        global ALLOW_REAL_ACTIONS
        ALLOW_REAL_ACTIONS = allow_real
        logger.info(f"Security Mode Update: Real Actions Allowed = {ALLOW_REAL_ACTIONS}")

    def execute(self, action_type: str, params: any, mode: str = "SIMULATED") -> dict:
        """
        Executes or Simulates an action.
        mode can be 'REAL' or 'SIMULATED'.
        Even if mode is REAL, ALLOW_REAL_ACTIONS must be True to execute.
        """
        # Global override
        global ALLOW_REAL_ACTIONS
        
        # Decide if we really execute
        # Logic: 
        #   If request says SIMULATED -> Simulate.
        #   If request says REAL:
        #       Check global ALLOW_REAL_ACTIONS. 
        #       If True -> Execute.
        #       If False -> Deny or Simulate (we deny for safety).
        
        should_execute = False
        if mode == "REAL":
            if ALLOW_REAL_ACTIONS:
                should_execute = True
            else:
                return {"status": "denied", "reason": "Global Safety Lock is ON"}
        
        logger.info(f"Processing Action: {action_type} Params: {params} Mode: {mode} Executing: {should_execute}")

        if not should_execute:
            # Simulation Only
            time.sleep(0.5) # Fake latency
            return {"status": "simulated", "action": action_type, "detail": "Action handled in simulation mode."}

        # REAL EXECUTION
        try:
            if action_type == "OPEN_APP":
                app_name = params
                # Simple unsafe implementation for demo (v1.8)
                # In prod, validate against whitelist
                if app_name.lower() == "notepad":
                    subprocess.Popen("notepad.exe")
                elif app_name.lower() == "calc":
                    subprocess.Popen("calc.exe")
                else:
                    return {"status": "failed", "reason": f"App '{app_name}' not in whitelist"}
                
                return {"status": "success", "detail": f"Opened {app_name}"}

            elif action_type == "TYPE_TEXT":
                text = params
                pyautogui.write(text, interval=0.05)
                return {"status": "success", "detail": f"Typed {len(text)} chars"}
                
            elif action_type == "MOUSE_MOVE":
                x = params.get("x", 0)
                y = params.get("y", 0)
                pyautogui.moveTo(x, y, duration=0.5)
                return {"status": "success", "detail": f"Moved to {x},{y}"}

            elif action_type == "CLICK":
                pyautogui.click()
                return {"status": "success", "detail": "Clicked"}

            else:
                return {"status": "error", "reason": f"Unknown action: {action_type}"}

        except Exception as e:
            logger.error(f"Execution Error: {e}")
            return {"status": "error", "reason": str(e)}

action_executor = ActionExecutor()
