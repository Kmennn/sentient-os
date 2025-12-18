import pytest
from brain.autonomy.trust_model import TrustModel, TrustTier

def test_global_trust_still_works():
    tm = TrustModel(initial_score=0.6)
    assert tm.get_tier() == TrustTier.MEDIUM
    
    # Success boosts global
    tm.update("SUCCESS") 
    # 0.6 + 0.05 = 0.65 (Medium)
    assert tm.get_tier() == TrustTier.MEDIUM
    
    # Critical failure tanks it
    tm.update("CRITICAL_FAILURE")
    # 0.65 - 0.3 = 0.35 (Low)
    assert tm.get_tier() == TrustTier.LOW

def test_user_scoping():
    tm = TrustModel(initial_score=0.9) # High trust system
    user_id = "bad_actor"
    
    # User causes critical failure
    tm.update("CRITICAL_FAILURE", user_id=user_id)
    
    # System takes a hit
    # 0.9 - 0.3 = 0.6 (Medium)
    assert tm.score == pytest.approx(0.6)
    
    # User takes a hit
    # Default 1.0 - 0.2 = 0.8
    assert tm.user_scores[user_id] == pytest.approx(0.8)
    
    # Effective score for this user:
    # 0.6 * 0.8 = 0.48 (Low Tier)
    assert tm.get_effective_score(user_id) == pytest.approx(0.48)
    assert tm.get_tier(user_id) == TrustTier.LOW
    
    # Another user (innocent)
    # Effective score: 0.6 * 1.0 = 0.6 (Medium Tier)
    assert tm.get_tier("innocent_user") == TrustTier.MEDIUM

def test_trust_rebuild():
    tm = TrustModel(initial_score=0.5)
    user_id = "recovering_user"
    tm.user_scores[user_id] = 0.5 # Start them low
    
    tm.update("SUCCESS", user_id=user_id)
    
    # Global up: 0.5 + 0.05 = 0.55
    # User up: 0.5 + 0.01 = 0.51
    
    assert tm.score == pytest.approx(0.55)
    assert tm.user_scores[user_id] == pytest.approx(0.51)
