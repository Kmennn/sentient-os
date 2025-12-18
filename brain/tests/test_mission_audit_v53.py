import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_reflection_logging():
    audit = MissionAudit()
    audit.log_reflection("SHOWN", "id-123")
    
    trace = audit.traces["reflection_log"]
    evt = trace["events"][0]
    assert evt["type"] == "REFLECTION_USAGE"
    assert evt["details"]["action"] == "SHOWN"
    assert evt["details"]["prompt_id"] == "id-123"
