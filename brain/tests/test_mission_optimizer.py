import pytest
from brain.optimization.mission_optimizer import MissionOptimizer, OptimizationAction
from brain.memory.mission_memory import MissionMemory
from brain.missions.mission_outcome import MissionOutcome, MissionStatus

@pytest.fixture
def memory():
    return MissionMemory()

@pytest.fixture
def optimizer(memory):
    return MissionOptimizer(memory)

def test_no_hints_initially(optimizer):
    hints = optimizer.analyze_history("cleaning")
    assert len(hints) == 0

def test_consecutive_failure_hints(memory, optimizer):
    # Add 2 failures
    for i in range(2):
        memory.add_outcome(MissionOutcome(
            mission_id=f"f{i}",
            mission_type="cleaning",
            status=MissionStatus.FAILURE,
            duration=5.0,
            failure_reason="Busy",
            resource_contention=["camera_main"]
        ))
        
    hints = optimizer.analyze_history("cleaning")
    
    # Should suggest delay
    delay_hints = [h for h in hints if h.action == OptimizationAction.SCHEDULE_DELAY]
    assert len(delay_hints) == 1
    assert delay_hints[0].parameter >= 10.0 # 5.0 * 2
    
    # Should suggest concurrency avoidance due to camera_main
    concurrency_hints = [h for h in hints if h.action == OptimizationAction.AVOID_CONCURRENCY]
    assert len(concurrency_hints) == 1
    assert concurrency_hints[0].related_resource == "camera_main"

def test_success_clears_hints(memory, optimizer):
    # Fail then Success
    memory.add_outcome(MissionOutcome("f1", "cleaning", MissionStatus.FAILURE, 5.0))
    memory.add_outcome(MissionOutcome("s1", "cleaning", MissionStatus.SUCCESS, 5.0))
    
    # outcomes are Newest First in get_outcomes?
    # MissionMemory logic: append adds to end. get_outcomes returns reversed (newest first).
    # So [Success, Failure].
    # Consecutive failures = 0 (first is success).
    
    hints = optimizer.analyze_history("cleaning")
    assert len(hints) == 0
