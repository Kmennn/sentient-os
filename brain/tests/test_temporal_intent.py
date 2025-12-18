import pytest
import time
from brain.intents.temporal_intent import TemporalIntent, TimeFlexibility
from brain.auth.role import UserRole

def test_temporal_validity():
    # Future start
    ti = TemporalIntent(
        user_id="u1", role=UserRole.OPERATOR, description="Future",
        earliest_start=time.time() + 100
    )
    assert not ti.can_start_now()
    assert not ti.is_expired()
    
    # Valid window
    ti2 = TemporalIntent(
        user_id="u2", role=UserRole.OPERATOR, description="Now",
        earliest_start=time.time() - 10,
        expiry=time.time() + 100
    )
    assert ti2.can_start_now()
    assert not ti2.is_expired()

def test_expiry_checks():
    # Expired by latest_start
    ti = TemporalIntent(
        user_id="u3", role=UserRole.OPERATOR, description="Late",
        latest_start=time.time() - 10
    )
    assert ti.is_expired()
    
    # Expired by expiry
    ti2 = TemporalIntent(
        user_id="u4", role=UserRole.OPERATOR, description="Expired",
        expiry=time.time() - 10
    )
    assert ti2.is_expired()
