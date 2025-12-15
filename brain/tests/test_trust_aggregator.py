
import pytest
from brain.autonomy.trust_aggregator import TrustAggregator, TrustTier

def test_aggregation():
    agg = TrustAggregator()
    
    # Mission A is good
    agg.register_mission("A")
    tm_a = agg.get_mission_trust("A")
    # Score 0.5 start? TrustModel default is 0.5 in v4.1?
    # Let's check TrustModel default. It was 0.5 -> Medium.
    assert agg.get_global_trust_score() == 0.5
    
    # Boost A
    for _ in range(10): tm_a.update('SUCCESS')
    assert tm_a.score > 0.8
    assert agg.get_global_trust_score() > 0.8 # Only A exists
    assert agg.get_global_tier() == TrustTier.HIGH
    
    # Mission B joins (Starts at 0.5)
    agg.register_mission("B")
    tm_b = agg.get_mission_trust("B")
    
    # Global should drop to min(A, B) = 0.5
    assert agg.get_global_trust_score() == 0.5
    assert agg.get_global_tier() == TrustTier.MEDIUM
    
    # B fails
    tm_b.update('FAILURE')
    assert agg.get_global_trust_score() < 0.5
    assert agg.get_global_tier() == TrustTier.LOW
