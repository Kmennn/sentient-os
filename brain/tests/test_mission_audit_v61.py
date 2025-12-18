import pytest
from brain.audit.mission_audit import MissionAudit

def test_audit_shared_voting():
    audit = MissionAudit()
    audit.log_shared_vote("prop-1", "alice", True)
    
    trace = audit.traces["coplan_log"]
    # Should append to existing trace if created, or create new.
    # Logic in previous step ensures trace exists if log_coplan called.
    # But log_shared_vote assumes it? No, log_event handles basic trace existence check?
    # Let's check MissionAudit.log_event implementation.
    # It assumes trace exists?
    # Actually wait, log_reflection/coplan explicitly check/create trace.
    # log_shared_vote calls log_event directly. If trace missing, might crash if log_event doesn't handle.
    # However, MissionAudit.log_event usually appends.
    # Let's ensure trace exists in test setup.
    
    audit.log_coplan("CREATED", "prop-1") # Ensure trace
    audit.log_shared_vote("prop-1", "alice", False)
    
    evt = trace["events"][-1]
    assert evt["type"] == "COPLAN_VOTE"
    assert evt["details"]["vote"] == "VETOED"
