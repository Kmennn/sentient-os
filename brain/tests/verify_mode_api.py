import requests
import time

BASE_URL = "http://localhost:8000"

def test_get_mode():
    print("Testing GET /system/mode...")
    try:
        resp = requests.get(f"{BASE_URL}/system/mode")
        resp.raise_for_status()
        print(f"Success: {resp.json()}")
        return resp.json()['mode']
    except Exception as e:
        print(f"FAILED: {e}")
        return None

def test_set_mode(mode):
    print(f"Testing POST /system/mode -> {mode}...")
    try:
        resp = requests.post(f"{BASE_URL}/system/mode", json={"mode": mode})
        resp.raise_for_status()
        print(f"Success: {resp.json()}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    print("--- Verifying Autonomy Mode API ---")
    current = test_get_mode()
    
    if current:
        test_set_mode("SIMULATION")
        time.sleep(1)
        test_get_mode()
        
        test_set_mode("REAL")
        time.sleep(1)
        test_get_mode()
        
        test_set_mode("OFF")
        time.sleep(1)
        test_get_mode()
