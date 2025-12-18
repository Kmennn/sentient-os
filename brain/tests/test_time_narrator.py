import pytest
import time
from brain.explainability.time_narrator import TimeNarrator
from brain.intents.deferral_engine import DeferralDecision, DeferralStrategy

def test_narrator_delay():
    tn = TimeNarrator()
    dec = DeferralDecision(DeferralStrategy.DELAY, new_start_time=time.time() + 600, reason="Busy")
    msg = tn.explain_deferral("Test Mission", dec)
    assert "Test Mission" in msg
    assert "delayed by" in msg
    assert "10.0 mins" in msg
    assert "Busy" in msg

def test_narrator_expire():
    tn = TimeNarrator()
    dec = DeferralDecision(DeferralStrategy.EXPIRE, reason="Too late")
    msg = tn.explain_deferral("Test Mission", dec)
    assert "EXPIRED" in msg
    assert "Too late" in msg
