import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_day_plan_logging():
    audit = MissionAudit()
    audit.log_day_plan_usage("GENERATED")
    
    trace = audit.traces["day_plan_log"]
    evt = trace["events"][0]
    assert evt["type"] == "DAY_PLAN_USAGE"
    assert evt["details"]["action"] == "GENERATED"
