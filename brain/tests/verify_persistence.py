import sys
import os
import time

sys.path.append(os.getcwd())

from brain.persistence.device_registry_store import DeviceRegistryStore
from brain.devices.device_registry import DeviceRegistry
from brain.devices.device_identity import DeviceIdentity, DeviceType

def verify_persistence():
    print("=== PERSISTENCE CHECK ===")
    
    # 1. Setup Fresh
    store = DeviceRegistryStore("data/test_registry.json")
    if os.path.exists(store.file_path):
        os.remove(store.file_path)
        
    registry = DeviceRegistry()
    registry.register_heartbeat("d1", "desktop", ["TOAST"])
    registry.register_heartbeat("d2", "mobile", ["PANEL"])
    
    print(f"Created Registry with 2 devices.")
    
    # 2. Save
    store.save(registry)
    print("Saved to disk.")
    
    # 3. Simulate Restart (Destroy object)
    del registry
    
    # 4. Load
    restored = store.load()
    assert restored is not None, "Failed to load"
    assert len(restored._devices) == 2, f"Expected 2 devices, got {len(restored._devices)}"
    
    d1 = restored._devices["d1"]
    assert d1.device_type == DeviceType.DESKTOP
    assert "TOAST" in d1.capabilities
    
    print("PASS: Restored core data.")
    
    # Clean up
    if os.path.exists(store.file_path):
        os.remove(store.file_path)
    print("Cleanup done.")

if __name__ == "__main__":
    verify_persistence()
