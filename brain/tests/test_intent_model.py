import pytest
import time
from brain.intents.intent import Intent, IntentPriority
from brain.auth.role import UserRole

def test_intent_priority_comparison():
    # IntEnum allows direct integer comparison
    assert IntentPriority.EMERGENCY > IntentPriority.USER
    assert IntentPriority.USER > IntentPriority.BACKGROUND

def test_resource_overlap():
    i1 = Intent(user_id="u1", role=UserRole.OPERATOR, description="A", resources=["camera", "mic"])
    i2 = Intent(user_id="u2", role=UserRole.OPERATOR, description="B", resources=["mic", "speaker"])
    i3 = Intent(user_id="u3", role=UserRole.OPERATOR, description="C", resources=["arm"])

    assert i1.overlaps_resource(i2) # Shared 'mic'
    assert not i1.overlaps_resource(i3)

def test_time_expiration():
    past_window = (time.time() - 100, time.time() - 50)
    i = Intent(user_id="u1", role=UserRole.OPERATOR, description="Old", time_window=past_window)
    assert i.is_expired()
    
    future_window = (time.time() + 50, time.time() + 100)
    i2 = Intent(user_id="u1", role=UserRole.OPERATOR, description="Future", time_window=future_window)
    assert not i2.is_expired()
