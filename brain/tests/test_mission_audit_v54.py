import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_simulation_logging():
    audit = MissionAudit()
    audit.log_simulation("RUN", "scen-001")
    
    trace = audit.traces["simulation_log"]
    evt = trace["events"][0]
    assert evt["type"] == "WHAT_IF_USAGE"
    assert evt["details"]["action"] == "RUN"
    assert evt["details"]["scenario_id"] == "scen-001"
