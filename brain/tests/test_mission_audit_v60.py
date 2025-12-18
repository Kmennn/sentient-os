import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_coplan_logging():
    audit = MissionAudit()
    audit.log_coplan("APPLIED", "prop-001")
    
    trace = audit.traces["coplan_log"]
    evt = trace["events"][0]
    assert evt["type"] == "COPLAN_ACTION"
    assert evt["details"]["action"] == "APPLIED"
    assert evt["details"]["proposal_id"] == "prop-001"
