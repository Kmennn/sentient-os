import sys
import os
import shutil
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.getcwd())

from brain.api.stream import app
from brain.missions.mission_scheduler import mission_scheduler
from brain.autonomy.autonomy_ledger import DecisionType
from brain.preferences.explicit_preference import ImportanceLevel

def verify_preferences():
    print("=== EXPLICIT PREFERENCE STORE CHECK ===")
    
    # Setup Paths & Clean
    test_pref_db = "brain_data/test_prefs.json"
    test_meaning_db = "brain_data/test_meaning_for_prefs.json"
    
    mission_scheduler.preference_store.persistence_path = test_pref_db
    mission_scheduler.meaning_memory.persistence_path = test_meaning_db
    
    if os.path.exists(test_pref_db): os.remove(test_pref_db)
    if os.path.exists(test_meaning_db): os.remove(test_meaning_db)
    
    mission_scheduler.preference_store._preferences = {}
    mission_scheduler.meaning_memory._meanings = {}
    
    # 1. Check Default Fallback (Meaning)
    print("\n--- Step 1: Check Fallback to Meaning ---")
    # Set meaning to High relevance
    # Relevance 0.8 -> High (0.6 - 0.9)
    mission_scheduler.meaning_memory._meanings["SECURITY"] = MagicMock(relevance_score=0.8)
    
    client = TestClient(app)
    res = client.get("/preferences/SECURITY")
    if res.status_code == 200:
        data = res.json()
        print(f"Effective Level: {data['effective']['level']}")
        if data['effective']['source'] == "INFERRED_MEANING" and data['effective']['level'] == "high":
            print("PASS: Fallback to Meaning correct.")
        else:
            print(f"FAIL: Fallback mismatch. Got {data['effective']}")
    else:
        print(f"FAIL: API Error {res.status_code}")
        
    # 2. Set Explicit Preference
    print("\n--- Step 2: Set Explicit Preference (Override) ---")
    # User sets SECURITY to LOW priority manually
    res = client.post("/preferences/domain", json={"domain": "SECURITY", "importance_level": "low"})
    if res.status_code == 200:
        print("PASS: Preference set.")
    else:
        print(f"FAIL: Set Error {res.text}")
        
    # 3. Verify Override
    res = client.get("/preferences/SECURITY")
    data = res.json()
    print(f"Effective Level: {data['effective']['level']} Source: {data['effective']['source']}")
    
    if data['effective']['source'] == "EXPLICIT_USER" and data['effective']['level'] == "low":
        print("PASS: Explicit Preference overrides Meaning.")
    else:
        print(f"FAIL: Override failed. {data}")
        
    # 4. Verify Ledger
    entries = mission_scheduler.autonomy_ledger.get_entries()
    has_event = any(e.decision_type == DecisionType.EXPLICIT_PREFERENCE_SET for e in entries)
    if has_event:
        print("PASS: Ledger event found.")
    else:
        print("FAIL: Ledger event missing.")

    # Cleanup
    if os.path.exists(test_pref_db): os.remove(test_pref_db)
    if os.path.exists(test_meaning_db): os.remove(test_meaning_db)

if __name__ == "__main__":
    verify_preferences()
