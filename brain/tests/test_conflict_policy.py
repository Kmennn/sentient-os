import pytest
from brain.governance.conflict_policy import ConflictPolicy, Resolution
from brain.intents.intent import Intent, IntentPriority
from brain.intents.conflict_detector import ConflictReport
from brain.auth.role import UserRole

def _make_report(new_role, old_role, new_pri=IntentPriority.USER):
    new = Intent(user_id="n", role=new_role, description="N", priority=new_pri)
    active = Intent(user_id="a", role=old_role, description="A", priority=IntentPriority.USER)
    return ConflictReport(new_intent=new, active_intent=active, reason="Testing", resources_involved=[])

def test_emergency_override():
    policy = ConflictPolicy()
    # Operator with EMERGENCY vs OWNER
    report = _make_report(UserRole.OPERATOR, UserRole.OWNER, IntentPriority.EMERGENCY)
    assert policy.resolve(report) == Resolution.OVERRIDE

def test_role_hierarchy():
    policy = ConflictPolicy()
    
    # Owner vs Operator -> Override
    assert policy.resolve(_make_report(UserRole.OWNER, UserRole.OPERATOR)) == Resolution.OVERRIDE
    
    # Operator vs Owner -> Reject
    assert policy.resolve(_make_report(UserRole.OPERATOR, UserRole.OWNER)) == Resolution.REJECT_NEW
    
    # Operator vs Observer -> Override
    assert policy.resolve(_make_report(UserRole.OPERATOR, UserRole.OBSERVER)) == Resolution.OVERRIDE

def test_equal_role_escalation():
    policy = ConflictPolicy()
    
    # Operator vs Operator -> Escalate
    assert policy.resolve(_make_report(UserRole.OPERATOR, UserRole.OPERATOR)) == Resolution.ESCALATE
    
    # Owner vs Owner -> Escalate (Safe default)
    assert policy.resolve(_make_report(UserRole.OWNER, UserRole.OWNER)) == Resolution.ESCALATE
