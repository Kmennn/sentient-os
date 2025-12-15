
import pytest
import json
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract

def test_audit_flow():
    audit = MissionAudit()
    contract = MissionContract(name="Test")
    
    audit.start_mission_log(contract)
    audit.log_event(contract.mission_id, "STEP", "Picked cup")
    
    json_str = audit.export_json(contract.mission_id)
    data = json.loads(json_str)
    
    assert data["contract"]["name"] == "Test"
    assert data["events"][0]["type"] == "STEP"
