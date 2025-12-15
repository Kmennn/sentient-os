
import pytest
from brain.autonomy.trust_model import TrustModel, TrustTier

def test_trust_scoring():
    tm = TrustModel(initial_score=0.5)
    assert tm.get_tier() == TrustTier.MEDIUM
    
    # Success -> Increase
    tm.update("SUCCESS")
    assert tm.score == 0.55
    
    # Many successes -> High Tier
    for _ in range(10): tm.update("SUCCESS")
    assert tm.get_tier() == TrustTier.HIGH
    
def test_trust_penalty():
    tm = TrustModel(initial_score=0.8)
    tm.update("CRITICAL_FAILURE")
    assert tm.score == 0.5
    tm.update("FAILURE")
    assert tm.score == 0.4
    assert tm.get_tier() == TrustTier.LOW
