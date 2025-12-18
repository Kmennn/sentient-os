import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_proactive_logging():
    audit = MissionAudit()
    # Ensure proactive log trace exists or auto-created
    # log_event creates trace if missing for given ID
    
    audit.log_proactive_suggestion("Morning Login", "SHOWN")
    
    trace = audit.traces["proactive_log"]
    events = trace["events"]
    
    evt = next(e for e in events if e["type"] == "PROACTIVE_SUGGESTION")
    assert evt["details"]["routine_name"] == "Morning Login"
    assert evt["details"]["action"] == "SHOWN"
