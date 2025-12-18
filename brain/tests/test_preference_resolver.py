import pytest
import time
from brain.intents.preference_resolver import PreferenceResolver
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance
from brain.intents.temporal_intent import TemporalIntent, TimeFlexibility
from brain.intents.conflict_detector import ConflictReport
from brain.auth.role import UserRole
from brain.intents.intent import Intent
from brain.intents.deferral_engine import DeferralStrategy

def _make_report(new_intent):
    active = Intent(user_id="a", role=UserRole.OPERATOR, description="A")
    return ConflictReport(new_intent=new_intent, active_intent=active, reason="Res", resources_involved=[])

def test_low_tolerance_rejection():
    resolver = PreferenceResolver()
    
    # Flexible intent, normally delayed 5 mins
    flex = TemporalIntent(
        user_id="u1", role=UserRole.OPERATOR, description="Flex",
        flexibility=TimeFlexibility.FLEXIBLE
    )
    
    prefs = SchedulingPreferences(user_id="u1", delay_tolerance=DelayTolerance.LOW)
    
    decision = resolver.resolve(_make_report(flex), prefs)
    
    # Engine would DELAY 300s. Tolerance LOW rejects > 60s.
    assert decision.strategy == DeferralStrategy.EXPIRE
    assert "LOW tolerance" in decision.reason

def test_high_tolerance_acceptance():
    resolver = PreferenceResolver()
    
    flex = TemporalIntent(
        user_id="u1", role=UserRole.OPERATOR, description="Flex",
        flexibility=TimeFlexibility.FLEXIBLE
    )
    
    prefs = SchedulingPreferences(user_id="u1", delay_tolerance=DelayTolerance.HIGH)
    
    decision = resolver.resolve(_make_report(flex), prefs)
    
    assert decision.strategy == DeferralStrategy.DELAY
