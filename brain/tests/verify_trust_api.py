import requests
import time

BASE_URL = "http://localhost:8011"

def test_trust_api():
    print("Testing GET /autonomy/trust...")
    try:
        resp = requests.get(f"{BASE_URL}/autonomy/trust")
        resp.raise_for_status()
        data = resp.json()
        print(f"Success: {data}")
        
        if "score" not in data or "tier" not in data:
            print("FAILED: Missing fields")
            return False
            
        if not (0.0 <= data["score"] <= 1.0):
            print("FAILED: Score out of range")
            return False
            
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    test_trust_api()
