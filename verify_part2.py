import requests
import time
import sys

BRAIN_URL = "http://localhost:8000"
BODY_URL = "http://localhost:8001"

def test_brain_body_connection():
    print("--- Verifying Brain -> Body Connectivity ---")
    
    # 1. Check Body Health
    try:
        resp = requests.get(f"{BODY_URL}/health")
        resp.raise_for_status()
        print(f"Body Health: {resp.json()}")
    except Exception as e:
        print(f"Body connection failed: {e}")
        return False

    # 2. Enable Real Actions on Body
    try:
        resp = requests.post(f"{BODY_URL}/admin/toggle-actions?enable=true")
        resp.raise_for_status()
        print(f"Body Actions Enabled: {resp.json()}")
    except Exception as e:
        print(f"Failed to enable actions: {e}")
        return False

    # 3. Enable Autonomy & Trigger Action via Brain
    # First, enable REAL mode to allow actions
    try:
        print("Enabling Autonomy (Mode: REAL)...")
        resp = requests.post(f"{BRAIN_URL}/system/mode", json={"mode": "REAL"})
        print(f"Mode Set: {resp.json()}")
    except Exception as e:
        print(f"Failed to set mode: {e}")
        return False

    # This simulates an Agent requesting "scroll_down"
    payload = {
        "action": "scroll_down",
        "params": {},
        "agent_id": "test_script"
    }
    
    print(f"Sending Action Request to Brain: {payload}")
    try:
        # Note: /action/request in routes.py calls Body's /action/run
        # But Body's /action/run implementation calls action_executor.execute
        # Let's check kernel.py: /action/execute is the one with "scroll_down" logic hardcoded for safety?
        # No, /action/run calls action_executor.
        # Let's check routes.py again.
        # routes.py calls BODY_URL/action/run with {"action": req.action, "params": req.params, "mode": mode}
        
        # We need to make sure "scroll_down" is a valid action for action_executor or the sandboxed "execute_action_endpoint".
        # routes.py calls /action/run. 
        # kernel.py /action/run calls action_executor.execute(action, params, mode)
        # We haven't checked action_executor.py.
        # However, kernel.py also has /action/execute (Safe Executor).
        
        # Wait, routes.py line 71: BODY_URL = "http://localhost:8001/action/run"
        # So it hits /action/run.
        
        # User said "Trigger ONE existing action... mouse move...".
        # I'll try "scroll_down" if it's supported.
        # Or I can try hitting /action/execute directly if I want to test "Safe Executor".
        # But verification requires Brain -> Body.
        # Brain calls /action/run.
        
        resp = requests.post(f"{BRAIN_URL}/action/request", json=payload)
        print(f"Brain Response: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "executed":
                print("SUCCESS: Action Executed.")
                return True
            else:
                 print(f"FAILURE: Status is {data.get('status')}")
                 return False
        else:
             print("FAILURE: Brain returned error.")
             return False

    except Exception as e:
        print(f"Test Failed: {e}")
        return False

if __name__ == "__main__":
    if test_brain_body_connection():
        sys.exit(0)
    else:
        sys.exit(1)
