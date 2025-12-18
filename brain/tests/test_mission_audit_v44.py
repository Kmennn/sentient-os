import pytest
import json
from brain.audit.mission_audit import MissionAudit
from brain.missions.mission_contract import MissionContract
from brain.auth.user import User
from brain.auth.role import UserRole

def test_audit_logs_approval():
    audit = MissionAudit()
    c = MissionContract()
    
    audit.start_mission_log(c)
    
    approver = User(name="Alice", role=UserRole.OWNER)
    
    audit.log_approval(
        mission_id=c.mission_id,
        approver_id=approver.user_id,
        approver_role=approver.role.name,
        approved=True,
        reason="Looks good"
    )
    
    trace = audit.traces[c.mission_id]
    events = trace["events"]
    
    approval_event = next(e for e in events if e["type"] == "APPROVAL_DECISION")
    assert approval_event["details"]["approver_id"] == approver.user_id
    assert approval_event["details"]["approver_role"] == "OWNER"
    assert approval_event["details"]["approved"] is True
    assert approval_event["details"]["reason"] == "Looks good"

def test_audit_persists_contract_creator():
    audit = MissionAudit()
    creator = User(name="Bob", role=UserRole.OPERATOR)
    c = MissionContract(created_by=creator.user_id)
    
    audit.start_mission_log(c)
    
    trace = audit.traces[c.mission_id]
    assert trace["contract"]["created_by"] == creator.user_id
