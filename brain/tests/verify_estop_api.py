import requests
import time

BASE_URL = "http://localhost:8012"

def test_estop_api():
    print("Testing POST /emergency/stop...")
    try:
        resp = requests.post(f"{BASE_URL}/emergency/stop")
        resp.raise_for_status()
        data = resp.json()
        print(f"Success: {data}")
        
        if data.get("status") != "STOPPED":
             print("FAILED: Status not STOPPED")
             return False
             
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    test_estop_api()
