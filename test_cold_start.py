import requests
import time

print("Waiting 20s for idle unload...")
time.sleep(20)
print("Sending request...")
try:
    r = requests.post("http://localhost:8000/chat", json={"message": "hi", "user_id": "test"})
    print(f"Response: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
