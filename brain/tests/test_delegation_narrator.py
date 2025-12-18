import pytest
import time
from brain.explainability.delegation_narrator import DelegationNarrator
from brain.auth.delegation import Delegation, DelegationScope

def test_delegation_narration():
    narrator = DelegationNarrator()
    d = Delegation.create("alice", "bob", DelegationScope.ALL, 3600)
    
    text = narrator.narrate_delegation(d)
    assert "Active" in text
    assert "alice -> bob" in text
    
    d.expires_at = time.time() - 10
    text = narrator.narrate_delegation(d)
    assert "Expired" in text
