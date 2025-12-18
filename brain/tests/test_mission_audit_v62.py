import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_delegation_logging():
    audit = MissionAudit()
    audit.log_delegation_used("prop-1", "bob", "alice")
    
    trace = audit.traces["coplan_log"]
    evt = trace["events"][-1]
    assert evt["type"] == "DELEGATION_USED"
    assert evt["details"]["delegate_id"] == "bob"
    assert evt["details"]["on_behalf_of"] == "alice"
