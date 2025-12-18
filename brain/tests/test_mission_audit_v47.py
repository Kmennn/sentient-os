import pytest
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract

def test_audit_preference_logging():
    audit = MissionAudit()
    c = MissionContract()
    audit.start_mission_log(c)
    
    audit.log_preference(c.mission_id, "delay_tolerance", "LOW")
    
    trace = audit.traces[c.mission_id]
    events = trace["events"]
    
    pref_event = next(e for e in events if e["type"] == "PREFERENCE_USED")
    assert pref_event["details"]["key"] == "delay_tolerance"
    assert pref_event["details"]["value"] == "LOW"
