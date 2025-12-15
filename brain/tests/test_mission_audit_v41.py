
import pytest
import json
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract

def test_audit_trust_recovery():
    audit = MissionAudit()
    contract = MissionContract(name="AuditV41")
    
    audit.start_mission_log(contract)
    audit.log_trust_change(contract.mission_id, "HIGH", "MEDIUM", 0.7)
    audit.log_recovery(contract.mission_id, 5)
    
    json_str = audit.export_json(contract.mission_id)
    data = json.loads(json_str)
    
    events = data["events"]
    assert events[0]["type"] == "TRUST_CHANGE"
    assert events[0]["details"]["new_tier"] == "MEDIUM"
    
    assert events[1]["type"] == "RECOVERY"
    assert events[1]["details"]["restored_at_step"] == 5
