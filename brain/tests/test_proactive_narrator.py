import pytest
from brain.proactive.proactive_policy import ProactivePolicy
from brain.explainability.proactive_narrator import ProactiveNarrator
from brain.autonomy.trust_model import TrustModel
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance
from brain.routines.routine import Routine

def test_policy_gate():
    policy = ProactivePolicy()
    trust = TrustModel()
    prefs = SchedulingPreferences("u1")
    
    # Trust 0.5 -> Allow
    assert policy.can_suggest("u1", trust, prefs)
    
    # Trust 0.1 -> Deny
    # Drop score below 0.2
    # Initial 0.5. Needs -0.3+.
    trust.update("CRITICAL_FAILURE", "u1") # -0.3 => 0.2
    trust.update("FAILURE", "u1") # -0.1 => 0.1
    
    # Verify score first to be sure
    assert trust.get_effective_score("u1") < 0.2
    
    assert not policy.can_suggest("u1", trust, prefs)

def test_narrator_styles():
    narrator = ProactiveNarrator()
    r = Routine("Lunch", 43200, 3600, [])
    
    msg_assertive = narrator.explain_suggestion(r, 'ASSERTIVE')
    assert "Heads up!" in msg_assertive
    
    msg_passive = narrator.explain_suggestion(r, 'PASSIVE')
    assert "Assistance available" in msg_passive
