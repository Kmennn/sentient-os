import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_load_logging():
    audit = MissionAudit()
    audit.log_load_insights("GENERATED")
    
    trace = audit.traces["load_insights_log"]
    evt = trace["events"][0]
    assert evt["type"] == "LOAD_INSIGHT_USAGE"
    assert evt["details"]["action"] == "GENERATED"
