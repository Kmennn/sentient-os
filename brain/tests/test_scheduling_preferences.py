import pytest
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance

def test_preference_defaults():
    p = SchedulingPreferences(user_id="u1")
    assert p.delay_tolerance == DelayTolerance.MEDIUM
    assert p.allow_preemption == False

def test_custom_preferences():
    p = SchedulingPreferences(
        user_id="u2",
        delay_tolerance=DelayTolerance.HIGH,
        allow_preemption=True
    )
    assert p.delay_tolerance == DelayTolerance.HIGH
    assert p.allow_preemption == True
