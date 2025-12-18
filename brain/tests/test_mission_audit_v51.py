import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_week_usage_lines():
    audit = MissionAudit()
    audit.log_week_insights("GENERATED", 3)
    
    trace = audit.traces["week_insights_log"]
    evt = trace["events"][0]
    assert evt["type"] == "WEEK_INSIGHTS_USAGE"
    assert evt["details"]["action"] == "GENERATED"
    assert evt["details"]["insight_count"] == 3
