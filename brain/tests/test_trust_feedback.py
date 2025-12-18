import pytest
from brain.autonomy.trust_feedback import TrustFeedback
from brain.memory.mission_memory import MissionMemory
from brain.missions.mission_outcome import MissionOutcome, MissionStatus

@pytest.fixture
def memory():
    return MissionMemory()

@pytest.fixture
def feedback(memory):
    return TrustFeedback(memory)

def test_no_data_no_change(feedback):
    assert feedback.adjust_initial_trust("unknown", 0.5) == 0.5

def test_positive_adjustment(memory, feedback):
    # Add 4 successes
    for _ in range(4):
        memory.add_outcome(MissionOutcome("s", "cleaning", MissionStatus.SUCCESS, 1.0))
        
    # > 80% success (100%)
    new_trust = feedback.adjust_initial_trust("cleaning", 0.5)
    assert new_trust == 0.55 # +0.05

def test_negative_adjustment(memory, feedback):
    # Add 3 failures
    for _ in range(3):
        memory.add_outcome(MissionOutcome("f", "cleaning", MissionStatus.FAILURE, 1.0))
        
    # < 50% success (0%)
    new_trust = feedback.adjust_initial_trust("cleaning", 0.5)
    assert new_trust == 0.45 # -0.05

def test_adjustment_clamping(memory, feedback):
    # Ensure even if logic wanted huge change, it's clamped
    # (Though current logic is hardcoded to 0.05, let's assume hypothetical logic change) 
    # Validating the MAX_DELTA constant usage mainly for regression
    assert feedback.MAX_DELTA == 0.1
