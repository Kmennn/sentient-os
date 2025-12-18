import pytest
from brain.reflection.reflection_trigger import ReflectionTrigger
from brain.reflection.reflection_prompt import PromptType
from brain.load.load_model import LoadSnapshot, LoadLevel
from brain.week.week_plan import WeekPlan, WeeklyPattern

def test_trigger_high_load_streak():
    trigger = ReflectionTrigger()
    
    # 2 days of HIGH load
    snaps = [
        LoadSnapshot("2023-01-01", LoadLevel.HIGH, 90, "Heavy"),
        LoadSnapshot("2023-01-02", LoadLevel.HIGH, 95, "Heavy")
    ]
    
    wk = WeekPlan("2023-01-01")
    
    prompt = trigger.check_triggers(wk, snaps)
    
    assert prompt is not None
    assert prompt.type == PromptType.LOAD
    assert "consecutive days" in prompt.pattern_description

def test_trigger_conflict_pattern():
    trigger = ReflectionTrigger()
    snaps = [] # No load issues
    
    wk = WeekPlan("2023-01-01")
    wk.patterns.append(WeeklyPattern("CONFLICT_PRONE", "Conflicts detected", confidence=0.9))
    
    prompt = trigger.check_triggers(wk, snaps)
    
    assert prompt is not None
    assert prompt.type == PromptType.CONFLICT
