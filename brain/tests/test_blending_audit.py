
import pytest
from brain.audit.blending_audit import BlendingAudit

def test_audit_logging():
    audit = BlendingAudit()
    audit.log_execution("plan1", 0.5, "Trace: ...")
    
    assert len(audit.logs) == 1
    assert audit.logs[0]["alpha"] == 0.5
