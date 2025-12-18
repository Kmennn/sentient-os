import pytest
from brain.missions.mission_outcome import MissionOutcome, MissionStatus

def test_mission_outcome_creation():
    outcome = MissionOutcome(
        mission_id="mission_123",
        mission_type="cleaning",
        status=MissionStatus.SUCCESS,
        duration=12.5
    )
    assert outcome.mission_id == "mission_123"
    assert outcome.status == MissionStatus.SUCCESS
    assert outcome.duration == 12.5
    assert outcome.retries == 0  # Default

def test_mission_outcome_immutability():
    outcome = MissionOutcome(
        mission_id="mission_123",
        mission_type="cleaning",
        status=MissionStatus.SUCCESS,
        duration=12.5
    )
    with pytest.raises(AttributeError):
        outcome.status = MissionStatus.FAILURE

def test_mission_outcome_failure_fields():
    outcome = MissionOutcome(
        mission_id="mission_fail",
        mission_type="patrol",
        status=MissionStatus.FAILURE,
        duration=5.0,
        failure_reason="Obstructed",
        resource_contention=["camera_1"]
    )
    assert outcome.failure_reason == "Obstructed"
    assert "camera_1" in outcome.resource_contention
