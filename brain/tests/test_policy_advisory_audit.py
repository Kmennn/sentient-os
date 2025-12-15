
import pytest
from brain.audit.policy_advisory_audit import AdvisoryAudit

def test_audit_logging():
    audit = AdvisoryAudit()
    audit.log_event("SUBMIT", "id123", {"param": "lift", "delta": 0.1})
    
    assert len(audit.logs) == 1
    assert audit.logs[0]["action"] == "SUBMIT"
