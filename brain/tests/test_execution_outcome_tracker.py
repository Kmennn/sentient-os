
import pytest
import time
from brain.manipulation.outcomes.execution_outcome_tracker import ExecutionOutcomeTracker, OutcomeStatus

def test_recording():
    tracker = ExecutionOutcomeTracker()
    tracker.record_outcome(OutcomeStatus.SUCCESS, "zone_A", "All good", 1.5)
    
    assert len(tracker.history) == 1
    assert tracker.history[0].status == OutcomeStatus.SUCCESS

def test_stats():
    tracker = ExecutionOutcomeTracker()
    # 1 Success
    tracker.record_outcome(OutcomeStatus.SUCCESS, "zone_A")
    # 1 Failure
    tracker.record_outcome(OutcomeStatus.COLLISION, "zone_A")
    # 1 Success
    tracker.record_outcome(OutcomeStatus.SUCCESS, "zone_A")
    
    stats = tracker.get_zone_stats("zone_A")
    assert stats["total"] == 3
    # 1 failure / 3 total = 0.33
    assert abs(stats["failure_rate"] - 0.333) < 0.01

def test_empty_zone():
    tracker = ExecutionOutcomeTracker()
    stats = tracker.get_zone_stats("void")
    assert stats["total"] == 0
