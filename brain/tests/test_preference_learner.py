import pytest
from brain.preferences.preference_learner import PreferenceLearner, UserAction
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance

def test_decrease_tolerance():
    learner = PreferenceLearner()
    prefs = SchedulingPreferences("u1", delay_tolerance=DelayTolerance.HIGH)
    
    # User cancels delay -> Drop to MED
    changed = learner.update(prefs, UserAction.CANCELLED_DELAY)
    assert changed
    assert prefs.delay_tolerance == DelayTolerance.MEDIUM
    
    # Again -> Drop to LOW
    changed = learner.update(prefs, UserAction.CANCELLED_DELAY)
    assert changed
    assert prefs.delay_tolerance == DelayTolerance.LOW
    
    # Again -> Stay LOW
    changed = learner.update(prefs, UserAction.CANCELLED_DELAY)
    assert not changed
    assert prefs.delay_tolerance == DelayTolerance.LOW

def test_no_change_on_accept():
    learner = PreferenceLearner()
    prefs = SchedulingPreferences("u1", delay_tolerance=DelayTolerance.MEDIUM)
    
    changed = learner.update(prefs, UserAction.ACCEPTED_DELAY)
    assert not changed
    assert prefs.delay_tolerance == DelayTolerance.MEDIUM
