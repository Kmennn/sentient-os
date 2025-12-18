import pytest
import time
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract

def test_audit_deferral_logging():
    audit = MissionAudit()
    c = MissionContract()
    audit.start_mission_log(c)
    
    future = time.time() + 300
    audit.log_deferral(c.mission_id, future, "Conflict")
    
    trace = audit.traces[c.mission_id]
    events = trace["events"]
    
    defer_event = next(e for e in events if e["type"] == "MISSION_DEFERRED")
    assert defer_event["details"]["new_start_time"] == future
    assert defer_event["details"]["reason"] == "Conflict"
