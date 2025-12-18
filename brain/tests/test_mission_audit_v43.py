import pytest
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract
from brain.missions.mission_scheduler import MissionPriority

@pytest.fixture
def audit():
    return MissionAudit()

def test_log_hints(audit):
    # Mock contract needed to start log
    contract = MissionContract(mission_id="m1", name="cleaning")
    audit.start_mission_log(contract)
    
    from collections import namedtuple
    Hint = namedtuple('Hint', ['action', 'reason', 'parameter'])
    Action = namedtuple('Action', ['name'])
    
    hints = [
        Hint(Action("DELAY"), "Too many failures", 5.0)
    ]
    
    audit.log_hints("m1", hints)
    
    trace = audit.traces["m1"]
    event = trace["events"][0]
    assert event["type"] == "OPTIMIZATION_HINTS"
    assert event["details"][0]["action"] == "DELAY"
    assert event["details"][0]["parameter"] == 5.0

def test_log_trust_init(audit):
    contract = MissionContract(mission_id="m2", name="cleaning")
    audit.start_mission_log(contract)
    
    audit.log_trust_init("m2", 0.5, 0.05, 0.55)
    
    trace = audit.traces["m2"]
    event = trace["events"][0]
    assert event["type"] == "TRUST_INIT"
    assert event["details"]["base_trust"] == 0.5
    assert event["details"]["final_score"] == 0.55
