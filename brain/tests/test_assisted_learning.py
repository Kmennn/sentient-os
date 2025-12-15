
import pytest
from brain.manipulation.assisted_learning import LearningMonitor
from brain.manipulation.outcomes.execution_outcome_tracker import outcome_tracker, OutcomeStatus

def test_proposal_generation():
    lm = LearningMonitor()
    outcome_tracker.history = []
    
    # 2 failures
    outcome_tracker.record_outcome(OutcomeStatus.COLLISION, "zone_X")
    outcome_tracker.record_outcome(OutcomeStatus.COLLISION, "zone_X")
    
    proposal = lm.check_for_adaptations("zone_X")
    assert proposal is not None
    assert "Increase safety" in proposal["action"]
    assert lm.pending_adaptation is not None

def test_approval_flow(caplog):
    import logging
    caplog.set_level(logging.INFO)
    lm = LearningMonitor()
    lm.pending_adaptation = {"action": "Test"}
    
    # Approve
    lm.apply_adaptation(True)
    assert lm.pending_adaptation is None
    assert "APPROVED" in caplog.text
