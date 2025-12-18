import pytest
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract

def test_audit_conflict_logging():
    audit = MissionAudit()
    c = MissionContract() # mission_id generated
    audit.start_mission_log(c)
    
    conflict_data = {
        "reason": "Resource Contention",
        "opposing_mission": "m2",
        "resources": ["camera"]
    }
    
    audit.log_conflict(c.mission_id, conflict_data)
    
    trace = audit.traces[c.mission_id]
    events = trace["events"]
    
    conflict_event = next(e for e in events if e["type"] == "CONFLICT_DETECTED")
    assert conflict_event["details"]["reason"] == "Resource Contention"
    assert "camera" in conflict_event["details"]["resources"]
