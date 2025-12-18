import pytest
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract

def test_audit_routine_logging():
    audit = MissionAudit()
    c = MissionContract()
    audit.start_mission_log(c)
    
    audit.log_routine(c.mission_id, "Login Routine", "DETECTED")
    
    trace = audit.traces[c.mission_id]
    events = trace["events"]
    
    r_event = next(e for e in events if e["type"] == "ROUTINE_EVENT")
    assert r_event["details"]["routine_name"] == "Login Routine"
    assert r_event["details"]["action"] == "DETECTED"
