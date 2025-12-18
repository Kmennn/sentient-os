import pytest
import time
from brain.intents.deferral_engine import DeferralEngine, DeferralStrategy
from brain.intents.temporal_intent import TemporalIntent, TimeFlexibility
from brain.intents.intent import Intent
from brain.intents.conflict_detector import ConflictReport
from brain.auth.role import UserRole

def _make_report(new_intent):
    active = Intent(user_id="a", role=UserRole.OPERATOR, description="A")
    return ConflictReport(new_intent=new_intent, active_intent=active, reason="Res", resources_involved=[])

def test_strict_expiry():
    engine = DeferralEngine()
    strict = TemporalIntent(
        user_id="u1", role=UserRole.OPERATOR, description="Strict",
        flexibility=TimeFlexibility.STRICT
    )
    decision = engine.evaluate(_make_report(strict))
    assert decision.strategy == DeferralStrategy.EXPIRE

def test_flexible_deferral():
    engine = DeferralEngine()
    flex = TemporalIntent(
        user_id="u1", role=UserRole.OPERATOR, description="Flex",
        flexibility=TimeFlexibility.FLEXIBLE
    )
    decision = engine.evaluate(_make_report(flex))
    assert decision.strategy == DeferralStrategy.DELAY
    assert decision.new_start_time > time.time()

def test_flexible_expiry_constraint():
    engine = DeferralEngine()
    # Latest start is 1 second from now. Delay (300s) would exceed it.
    flex = TemporalIntent(
        user_id="u1", role=UserRole.OPERATOR, description="Flex but tight",
        flexibility=TimeFlexibility.FLEXIBLE,
        latest_start=time.time() + 1
    )
    decision = engine.evaluate(_make_report(flex))
    assert decision.strategy == DeferralStrategy.EXPIRE
