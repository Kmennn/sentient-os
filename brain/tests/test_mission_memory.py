import pytest
from brain.memory.mission_memory import MissionMemory
from brain.missions.mission_outcome import MissionOutcome, MissionStatus

@pytest.fixture
def memory():
    return MissionMemory()

def test_add_and_retrieve_outcome(memory):
    outcome = MissionOutcome(
        mission_id="m1",
        mission_type="cleaning",
        status=MissionStatus.SUCCESS,
        duration=10.0
    )
    memory.add_outcome(outcome)
    
    results = memory.get_outcomes("cleaning")
    assert len(results) == 1
    assert results[0].mission_id == "m1"

def test_stats_calculation(memory):
    # Add 1 SUCCESS, 1 FAILURE
    memory.add_outcome(MissionOutcome("m1", "repair", MissionStatus.SUCCESS, 10.0))
    memory.add_outcome(MissionOutcome("m2", "repair", MissionStatus.FAILURE, 20.0))
    
    stats = memory.get_stats("repair")
    assert stats["sample_size"] == 2
    assert stats["success_rate"] == 0.5
    assert stats["avg_duration"] == 15.0

def test_empty_stats(memory):
    stats = memory.get_stats("unknown_type")
    assert stats["sample_size"] == 0
    assert stats["success_rate"] == 0.0
