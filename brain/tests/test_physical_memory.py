
import pytest
from brain.memory.physical_memory import PhysicalMemory
from brain.manipulation.outcomes.execution_outcome_tracker import outcome_tracker, OutcomeStatus

def test_adaptive_clearance():
    mem = PhysicalMemory()
    # Mock Tracker History
    outcome_tracker.history = []
    
    # Clean state
    assert mem.get_suggested_clearance("zone_B") == 0.1
    
    # Add failures
    outcome_tracker.record_outcome(OutcomeStatus.COLLISION, "zone_B")
    outcome_tracker.record_outcome(OutcomeStatus.COLLISION, "zone_B")
    outcome_tracker.record_outcome(OutcomeStatus.SUCCESS, "zone_B")
    # Rate = 0.66
    
    suggested = mem.get_suggested_clearance("zone_B")
    assert suggested == 0.2 # 2x base

def test_moderate_adaptation():
    mem = PhysicalMemory()
    outcome_tracker.history = []
    
    # 1 fail, 3 success (Rate 0.25)
    outcome_tracker.record_outcome(OutcomeStatus.COLLISION, "zone_C")
    outcome_tracker.record_outcome(OutcomeStatus.SUCCESS, "zone_C")
    outcome_tracker.record_outcome(OutcomeStatus.SUCCESS, "zone_C")
    outcome_tracker.record_outcome(OutcomeStatus.SUCCESS, "zone_C")
    
    suggested = mem.get_suggested_clearance("zone_C")
    assert abs(suggested - 0.15) < 0.001 # 1.5x base
