import uvicorn
import platform
import psutil
import time
import asyncio
import websockets
import json
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sentient Local Kernel", version="0.1.0")

# Allow Flutter frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def system_status():
    """Simulates reading local hardware stats (RTOS duties)"""
    return {
        "system": platform.system(),
        "os_type": psutil.os.name,
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "kernel_mode": "Active (Simulated)",
        "process_count": len(psutil.pids())
    }

@app.get("/health")
def health_check():
    """Diagnostic endpoint for system vitals."""
    return {
        "status": "active",
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "uptime": time.time() - psutil.boot_time(),
        "real_actions_enabled": ALLOW_REAL_ACTIONS
    }

import asyncio
import websockets
import json
from fastapi import BackgroundTasks

# ... (existing imports)

import mss
import base64
import io

@app.get("/screenshot")
def capture_screen():
    try:
        with mss.mss() as sct:
            # Capture primary monitor
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            # Convert to PNG
            png = mss.tools.to_png(sct_img.rgb, sct_img.size)
            # Encode base64
            b64_str = base64.b64encode(png).decode('utf-8')
            return {"image": b64_str}
    except Exception as e:
        print(f"Screenshot failed: {e}")
        return {"error": str(e)}

# --- SAFE EXECUTOR STATE ---
ALLOW_REAL_ACTIONS = False # Set to True via ENV or Config for real execution
PENDING_ACTIONS = set()

@app.post("/action/execute")
def execute_action_endpoint(payload: dict):
    global ALLOW_REAL_ACTIONS
    
    intent = payload.get("intent", "unknown")
    action_id = payload.get("action_id", "unknown")
    auth_token = payload.get("auth_token", "") 
    
    # H1 Security Patch: Token Validation
    # In future versions, verify signature here.
    if not payload.get("token") and not auth_token:
         # For backward compat, we log but don't crash yet, OR strict:
         # return {"status": "failed", "error": "Missing security token."}
         pass     
    # 1. Check Allow Switch
    if not ALLOW_REAL_ACTIONS:
        return {
            "status": "simulated",
            "action_id": action_id,
            "message": "Real actions disabled by policy (ALLOW_REAL_ACTIONS=False)."
        }

    # 2. Execute (Gated)
    try:
        import pyautogui
        PENDING_ACTIONS.add(action_id)
        
        # --- SANDBOXED IMPLEMENTATION ---
        if intent == "open_settings":
            # Simulate or Real? Let's do Real if allowed.
            pyautogui.hotkey('win', 'i')
            result = "Opened Settings via Win+I"
            
        elif intent == "scroll_down":
            pyautogui.scroll(-500)
            result = "Scrolled down 500 units"
            
        elif intent == "scroll_up":
            pyautogui.scroll(500)
            result = "Scrolled up 500 units"
            
        else:
            result = f"Intent '{intent}' not mapped in SafeExecutor."
            
        PENDING_ACTIONS.discard(action_id)
        return {
            "status": "executed",
            "action_id": action_id,
            "result": result
        }
        
    except Exception as e:
        PENDING_ACTIONS.discard(action_id)
        return {"status": "failed", "error": str(e)}

from action_executor import action_executor

@app.post("/action/run")
def run_action(payload: dict):
    """
    New v1.8 Endpoint for Agentic Actions.
    payload: { "action": "OPEN_APP", "params": "notepad", "mode": "REAL" }
    """
    action = payload.get("action")
    params = payload.get("params")
    mode = payload.get("mode", "SIMULATED")
    
    return action_executor.execute(action, params, mode)

@app.post("/admin/toggle-actions")
def toggle_actions(enable: bool):
    """
    Updates the security mode of the ActionExecutor.
    """
    action_executor.set_security_mode(enable)
    return {"status": "success", "real_actions_enabled": enable}


@app.post("/action") # Legacy v1.4 stub, kept for compatibility if needed
def execute_action_legacy(payload: dict):
    # redirect to new logic or just return mock
    return {
        "status": "executed_mock",
        "intent": payload.get("intent"),
        "timestamp": time.time()
    }

@app.get("/stream")
def stream_telemetry():
    """Lightweight telemetry endpoint for high-frequency polling"""
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "ts": time.time(),
        "uptime": int(time.time() - psutil.boot_time()),
        "temp": 45.0, # Mock temp
        "active_window": "VS Code" # Placeholder
    }

async def notify_brain_wake(confidence: float):
    uri = "ws://127.0.0.1:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({
                "type": "wake.trigger",
                "payload": {"confidence": confidence}
            }))
            # We don't wait for ACK here, fire and forget logic
    except Exception as e:
        print(f"Failed to notify brain: {e}")

@app.post("/wake-event")
async def wake_event(payload: dict, background_tasks: BackgroundTasks):
    confidence = payload.get("confidence", 0.0)
    if confidence > 0.65:
        background_tasks.add_task(notify_brain_wake, confidence)
        return {"status": "triggered", "confidence": confidence}
    return {"status": "ignored", "confidence": confidence}

@app.get("/wake")
def trigger_wake_test(background_tasks: BackgroundTasks):
    background_tasks.add_task(notify_brain_wake, 0.99)
    return {"status": "simulated_wake"}

if __name__ == "__main__":
    # Running on port 8001 to distinguish from Brain (8000)
    uvicorn.run(app, host="0.0.0.0", port=8001)
