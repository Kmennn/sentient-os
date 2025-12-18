import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_delegation_block():
    audit = MissionAudit()
    audit.log_coplan("CREATED", "p1") # Init Trace
    audit.log_delegation_blocked("p1", "bob", "BLOCKED_CHAIN")
    
    trace = audit.traces["coplan_log"]
    evt = trace["events"][-1]
    assert evt["type"] == "DELEGATION_BLOCKED"
    assert "CHAIN" in evt["details"]["reason"]
