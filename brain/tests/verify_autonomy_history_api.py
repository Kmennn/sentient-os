import sys
import os
import time

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType

def verify_api():
    print("=== AUTONOMY API CHECK ===")
    
    # 1. Setup Data
    # Reset Ledger for clean test
    test_ledger_path = "brain/api/autonomy_history_test.json"
    if os.path.exists(test_ledger_path):
        os.remove(test_ledger_path)
    
    mission_scheduler.autonomy_ledger.persistence_path = test_ledger_path
    mission_scheduler.autonomy_ledger._entries = []

    # Mock Services
    from unittest.mock import MagicMock
    mission_scheduler.scheduler_service = MagicMock()
    mission_scheduler.scheduler_service.get_protected_routines.return_value = []
    if "test_dev" not in mission_scheduler.device_registry._devices:
         mission_scheduler.device_registry.register_heartbeat("test_dev", "desktop", [])
    
    # Generate 3 events
    # Event 1: Suggested
    mission_scheduler._log_autonomy_decision(DecisionType.SUGGESTED, "s1", "a1", "msg1")
    time.sleep(0.01)
    # Event 2: Accepted
    mission_scheduler._log_autonomy_decision(DecisionType.ACCEPTED, "s1", "a1", "")
    time.sleep(0.01)
    # Event 3: Auto-Executed
    mission_scheduler._log_autonomy_decision(DecisionType.AUTO_EXECUTED, "s2", "a2", "Policy", was_auto=True)
    
    # 2. Call API
    client = TestClient(app)
    response = client.get("/autonomy/history?limit=10")
    
    if response.status_code != 200:
        print(f"FAIL: API Error {response.status_code}")
        return
        
    data = response.json()
    print(f"Entries Returned: {len(data)}")
    
    if len(data) != 3:
        print("FAIL: Expected 3 entries.")
        return
        
    # Check Sort Order (Newest First)
    if data[0]['decision_type'] != "auto_executed":
        print(f"FAIL: Expeceted auto_executed first, got {data[0]['decision_type']}")
        return
        
    # Check Filtering
    res_filter = client.get("/autonomy/history?decision_type=suggested")
    data_filter = res_filter.json()
    if len(data_filter) != 1 or data_filter[0]['decision_type'] != "suggested":
        print("FAIL: Filter failed.")
        return
        
    print("PASS: API returns correct data, sorted and filtered.")

if __name__ == "__main__":
    verify_api()
