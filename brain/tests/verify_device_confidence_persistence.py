import sys
import os
import time

sys.path.append(os.getcwd())

from brain.persistence.device_registry_store import DeviceRegistryStore
from brain.devices.device_registry import DeviceRegistry
from brain.devices.device_identity import DeviceIdentity, DeviceType
from brain.devices.device_confidence_manager import DeviceConfidenceManager

def verify_confidence_persistence():
    print("=== CONFIDENCE PERSISTENCE CHECK ===")
    
    file_path = "data/test_confidence_registry.json"
    
    # 1. Setup Fresh
    store = DeviceRegistryStore(file_path)
    if os.path.exists(store.file_path):
        os.remove(store.file_path)
        
    registry = DeviceRegistry()
    registry.register_heartbeat("d1", "desktop", ["TOAST"])
    manager = DeviceConfidenceManager(registry)
    
    # Check initial
    print(f"Initial Score: {manager.get_score('d1')}")
    assert 0.49 <= manager.get_score('d1') <= 0.51, "Initial should be ~0.5"
    
    # 2. Boost
    manager.register_interaction("d1") # +0.05
    manager.register_interaction("d1") # +0.05
    # Boost updates time, so score is fresh
    score = manager.get_score('d1')
    print(f"Boosted Score: {score}")
    assert score >= 0.58, "Should be boosted (~0.6)"
    
    # 3. Save
    store.save(registry)
    print("Saved to disk.")
    
    # 4. Simulate Restart
    del registry
    del manager
    
    # 5. Load
    restored_reg = store.load()
    restored_mgr = DeviceConfidenceManager(restored_reg)
    
    restored_score = restored_mgr.get_score('d1')
    print(f"Restored Score: {restored_score}")
    
    # Allow for minimal decay during exec time (microseconds)
    assert restored_score >= 0.58, "Confidence should be restored"
    
    # 6. Simulate Decay
    # Hack internal timestamp
    d1 = restored_reg._devices["d1"]
    d1.last_trust_update -= (10 * 60) # 10 mins ago
    
    decayed_score = restored_mgr.get_score('d1')
    print(f"Decayed Score (10m): {decayed_score}")
    
    assert decayed_score < restored_score, "Should have decayed"
    assert decayed_score < 0.6, "Should be lower"
    
    print("PASS: Confidence persisted and decays correctly.")
    
    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == "__main__":
    verify_confidence_persistence()
