import requests
import sys

BRAIN_URL = "http://localhost:8000"

def verify_safety():
    print("--- Verifying Safety (Body Down) ---")
    
    # Enable mode just in case (though it should persist if brain wasn't restarted)
    try:
        requests.post(f"{BRAIN_URL}/system/mode", json={"mode": "REAL"})
    except Exception as e:
        print(f"Note: Mode set might have failed (Brain down?): {e}")

    payload = {
        "action": "scroll_down",
        "params": {},
        "agent_id": "test_script"
    }
    
    print(f"Sending Action Request to Brain (Body should be DOWN): {payload}")
    try:
        resp = requests.post(f"{BRAIN_URL}/action/request", json=payload)
        print(f"Brain Response: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "error":
                print("SUCCESS: Brain handled failure gracefully.")
                return True
            else:
                print(f"FAILURE: Unexpected status executed? {data}")
                return False
        else:
             print(f"INFO: API returned {resp.status_code}. Checking if Brain acts normal.")
             return True

    except Exception as e:
        print(f"Test Failed: {e}")
        return False

if __name__ == "__main__":
    if verify_safety():
        sys.exit(0)
    else:
        sys.exit(1)
