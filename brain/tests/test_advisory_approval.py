
import pytest
from brain.learning.advisory_approval import AdvisoryApprovalManager, AdvisoryStatus
from brain.learning.policy_advisor import AdvisorySuggestion

def test_workflow():
    mgr = AdvisoryApprovalManager()
    sugg = AdvisorySuggestion("lift", 0.1, "Reason", "pol", 1.0)
    
    # Submit
    sid = mgr.submit_suggestion(sugg)
    assert sid in mgr.get_pending_suggestions()
    
    # Approve
    assert mgr.approve_suggestion(sid)
    assert sid not in mgr.get_pending_suggestions()
    assert len(mgr.get_approved_suggestions()) == 1
    
    # Cannot approve again (already approved - logic allows re-approve? Current logic just sets status. Returns True.)
    # Check status
    assert mgr._statuses[sid] == AdvisoryStatus.APPROVED

def test_rejection():
    mgr = AdvisoryApprovalManager()
    sugg = AdvisorySuggestion("lift", 0.1, "Reason", "pol", 1.0)
    sid = mgr.submit_suggestion(sugg)
    
    mgr.reject_suggestion(sid)
    assert len(mgr.get_approved_suggestions()) == 0
    assert mgr._statuses[sid] == AdvisoryStatus.REJECTED
