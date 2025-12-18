import pytest
from brain.explainability.preference_narrator import PreferenceNarrator
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance
from brain.intents.deferral_engine import DeferralDecision, DeferralStrategy

def test_explain_low_tolerance_rejection():
    narrator = PreferenceNarrator()
    prefs = SchedulingPreferences("u1", delay_tolerance=DelayTolerance.LOW)
    decision = DeferralDecision(DeferralStrategy.EXPIRE, reason="Delay exceeded LOW tolerance")
    
    msg = narrator.explain("My Mission", decision, prefs)
    
    assert "EXPIRED" in msg
    assert "Prevented delay" in msg
    assert "Low Tolerance" in msg

def test_explain_high_tolerance_allowance():
    narrator = PreferenceNarrator()
    prefs = SchedulingPreferences("u1", delay_tolerance=DelayTolerance.HIGH)
    # Mock time
    import time
    decision = DeferralDecision(DeferralStrategy.DELAY, new_start_time=time.time()+300, reason="Busy")
    
    msg = narrator.explain("My Mission", decision, prefs)
    
    assert "delayed" in msg
    assert "Allowed by your Preference" in msg
    assert "High Tolerance" in msg
