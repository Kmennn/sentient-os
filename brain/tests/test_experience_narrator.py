import pytest
from brain.explainability.experience_narrator import ExperienceNarrator
from brain.memory.mission_memory import MissionMemory
from brain.optimization.mission_optimizer import MissionOptimizer, OptimizationAction
from brain.missions.mission_outcome import MissionOutcome, MissionStatus

@pytest.fixture
def memory():
    return MissionMemory()

@pytest.fixture
def optimizer(memory):
    return MissionOptimizer(memory)

@pytest.fixture
def narrator(memory, optimizer):
    return ExperienceNarrator(memory, optimizer)

def test_no_experience(narrator):
    assert narrator.narrate_insights("unknown") == "No prior experience for 'unknown'."

def test_success_narrative(memory, narrator):
    memory.add_outcome(MissionOutcome("s1", "cleaning", MissionStatus.SUCCESS, 10.0))
    narrative = narrator.narrate_insights("cleaning")
    assert "Success rate: 100%" in narrative
    assert "Suggestions" not in narrative

def test_failure_narrative_with_hints(memory, narrator):
    # Add consecutive failures to trigger optimizer
    for i in range(2):
        memory.add_outcome(MissionOutcome(
            f"f{i}", "cleaning", MissionStatus.FAILURE, 5.0, 
            failure_reason="Obstructed", resource_contention=["cam"]
        ))
        
    narrative = narrator.narrate_insights("cleaning")
    
    assert "Success rate: 0%" in narrative
    assert "Most common error: Obstructed." in narrative
    assert "Suggestions:" in narrative
    # The optimizer should suggest Delay and Avoid Concurrency
    assert "Schedule Delay" in narrative
    assert "Avoid Concurrency" in narrative
