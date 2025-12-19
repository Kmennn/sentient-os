import sys
import os
import shutil
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from brain.memory.meaning_memory import InteractionType

sys.path.append(os.getcwd())

from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.external.external_signal import SignalSeverity

def verify_meaning():
    print("=== USER MEANING MEMORY CHECK ===")
    
    # Setup Paths & Clean
    test_db = "brain_data/test_meaning.json"
    mission_scheduler.meaning_memory.persistence_path = test_db
    if os.path.exists(test_db):
        os.remove(test_db)
        
    mission_scheduler.meaning_memory._meanings = {}
    mission_scheduler.autonomy_ledger._entries = []
    
    # Mock
    mission_scheduler.scheduler_service = MagicMock()
    
    # 1. Trigger ACK (Emergency)
    print("\n--- Step 1: Trigger ACK (Via Helper directly for simplicity or Mock API) ---")
    # API testing is better but requires complex dependency mocking for EmergencyManager. 
    # Let's test the helper method first as it's the core integration point used by API.
    # We can also call the API if we mock the manager properly.
    
    # Simulating API call logic:
    mission_scheduler.record_meaning_interaction("SECURITY", InteractionType.ACK, "test_ack")
    
    score = mission_scheduler.meaning_memory.get_relevance("SECURITY")
    print(f"SECURITY Score after ACK: {score}")
    
    if score > 0.5:
        print("PASS: Score increased.")
    else:
        print(f"FAIL: Score didn't increase: {score}")

    # 2. Trigger VIEW (Pattern)
    print("\n--- Step 2: Trigger VIEW ---")
    mission_scheduler.record_meaning_interaction("SYSTEM", InteractionType.VIEW, "test_view")
    
    score_sys = mission_scheduler.meaning_memory.get_relevance("SYSTEM")
    print(f"SYSTEM Score after VIEW: {score_sys}")
    
    if score_sys == 0.55: # Start 0.5 + 0.05
         print("PASS: Score increased slightly.")
    else:
         print(f"WARN: Expected 0.55, got {score_sys}")
         
    # 3. Trigger DISMISS
    print("\n--- Step 3: Trigger DISMISS ---")
    # Dismiss Security
    mission_scheduler.record_meaning_interaction("SECURITY", InteractionType.DISMISS, "test_dismiss")
    
    score_sec_2 = mission_scheduler.meaning_memory.get_relevance("SECURITY")
    print(f"SECURITY Score after DISMISS: {score_sec_2}")
    
    if score_sec_2 < score:
        print("PASS: Score decreased.")
    else:
        print("FAIL: Score didn't decrease.")
        
    # 4. Check API
    print("\n--- Step 4: Check API ---")
    client = TestClient(app)
    res = client.get("/memory/meaning")
    if res.status_code == 200:
        data = res.json()
        print(f"API Data: {data}")
        if data['count'] >= 2:
            print("PASS: Meanings returned.")
    else:
        print(f"FAIL: API Error {res.status_code}")

    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)

if __name__ == "__main__":
    verify_meaning()
