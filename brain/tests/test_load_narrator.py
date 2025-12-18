import pytest
from brain.explainability.load_narrator import LoadNarrator
from brain.load.load_policy import LoadPolicy
from brain.load.load_model import LoadSnapshot, LoadLevel

def test_narrator_neutrality():
    narrator = LoadNarrator()
    snap = LoadSnapshot("Today", LoadLevel.HIGH, 90, "Heavy")
    
    text = narrator.narrate(snap)
    assert "observation" in text.lower()
    # Ensure no emotional words like "Stress", "Fatigue" (manual check logic)
    assert "stress" not in text.lower()

def test_policy_trust_gate():
    policy = LoadPolicy()
    
    # Low trust -> Hide Low/Med
    assert policy.should_show_insight(LoadLevel.LOW, 0.1) is False
    assert policy.should_show_insight(LoadLevel.HIGH, 0.1) is True
    
    # High trust -> Show all
    assert policy.should_show_insight(LoadLevel.LOW, 0.8) is True
