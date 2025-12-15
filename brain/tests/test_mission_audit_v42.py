
import pytest
import os
import json
from brain.audit.mission_audit import MissionAudit

TEST_LOG_PATH = "brain/tests/data/audit_v42.jsonl"

from brain.missions.mission_contract import MissionContract, AutonomyLevel

@pytest.fixture
def audit():
    if os.path.exists(TEST_LOG_PATH):
        os.remove(TEST_LOG_PATH)
    return MissionAudit(log_path=TEST_LOG_PATH)

def test_audit_scheduling(audit):
    # Register mission first
    contract = MissionContract(name="MissionX", autonomy_level=AutonomyLevel.EXECUTE)
    audit.start_mission_log(contract)
    
    audit.log_scheduling(contract.mission_id, "PREEMPT", {"priority": 10})
    
    with open(TEST_LOG_PATH, 'r') as f:
        lines = f.readlines()
        # First line might be contract details or event?
        # start_mission_log DOES NOT write to file in current impl? 
        # Wait, start_mission_log just inits traces. 
        # log_event writes to file. 
        # So first line should be the event.
        line = json.loads(lines[0])
        assert line['event_type'] == "SCHEDULING"
        assert line['details']['action'] == "PREEMPT"

def test_audit_resource(audit):
    contract = MissionContract(name="MissionY", autonomy_level=AutonomyLevel.EXECUTE)
    audit.start_mission_log(contract)
    
    audit.log_resource_event(contract.mission_id, "arm_left", "ACQUIRED")
    
    with open(TEST_LOG_PATH, 'r') as f:
        line = json.loads(f.readline())
        assert line['event_type'] == "RESOURCE_LOCK"
        assert line['details']['resource'] == "arm_left"
