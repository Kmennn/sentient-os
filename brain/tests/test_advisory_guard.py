
import pytest
from brain.safety.advisory_guard import AdvisoryGuard
from brain.learning.policy_advisor import AdvisorySuggestion

def test_safe_suggestion():
    guard = AdvisoryGuard()
    # Current 0.05. Delta +0.1 = 0.15. Max 0.3. Safe.
    sugg = AdvisorySuggestion("lift_height", 0.1, "Reason", "pol1", 0.9)
    assert guard.validate_suggestion(sugg, {"lift_height": 0.05})

def test_unsafe_suggestion():
    guard = AdvisoryGuard()
    # Current 0.05. Delta +0.3 = 0.35. Max 0.3. Unsafe.
    sugg = AdvisorySuggestion("lift_height", 0.3, "Reason", "pol1", 0.9)
    assert not guard.validate_suggestion(sugg, {"lift_height": 0.05})
