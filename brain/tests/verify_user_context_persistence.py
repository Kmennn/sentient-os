import sys
import os
import time

sys.path.append(os.getcwd())

from brain.persistence.user_context_store import UserContextStore
from brain.learning.focus_pattern import FocusPattern, FocusPatternStatus
from brain.preferences.user_interrupt_settings import UserInterruptSettings
from brain.preferences.user_interrupt_schedule import UserInterruptSchedule
from brain.preferences.interrupt_style import InterruptStyle

def verify_user_context():
    print("=== USER CONTEXT PERSISTENCE CHECK ===")
    
    file_path = "data/test_user_context.json"
    
    # 1. Setup Fresh
    store = UserContextStore(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    # Create Dummy Data
    patterns = [
        FocusPattern("fp1", "09:00", "11:00", [0,1,2,3,4], confidence=0.9, status=FocusPatternStatus.APPROVED)
    ]
    
    settings = UserInterruptSettings("u1", InterruptStyle.NEVER_INTERRUPT)
    
    # Schedule default is created via factory usually, but let's confirm serialization
    schedule = UserInterruptSchedule.create_default("u1")
    
    manual_focus_expiry = time.time() + 3600 # 1 hour from now
    
    presence_override = "alone"
    
    # 2. Save
    store.save(
        focus_patterns=patterns,
        interrupt_settings=settings,
        interrupt_schedule=schedule,
        manual_focus_expiry=manual_focus_expiry,
        presence_override=presence_override
    )
    print("Saved to disk.")
    
    # 3. Simulate Restart
    del store
    
    # 4. Load
    store = UserContextStore(file_path)
    context = store.load()
    
    # 5. Verify
    print(f"Loaded Patterns: {len(context.focus_patterns)}")
    assert len(context.focus_patterns) == 1
    p = FocusPattern.from_dict(context.focus_patterns[0])
    assert p.pattern_id == "fp1"
    assert p.status == FocusPatternStatus.APPROVED
    
    print(f"Loaded Settings: {context.interrupt_settings}")
    s = UserInterruptSettings.from_dict(context.interrupt_settings)
    assert s.style == InterruptStyle.NEVER_INTERRUPT
    
    print(f"Loaded Manual Focus: {context.manual_focus_expiry}")
    # Allow small drift? No, exact float should persist via JSON dump
    assert abs(context.manual_focus_expiry - manual_focus_expiry) < 0.001
    
    print(f"Loaded Presence: {context.presence_override}")
    assert context.presence_override == "alone"
    
    print("PASS: User Context fully persisted.")
    
    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)

if __name__ == "__main__":
    verify_user_context()
