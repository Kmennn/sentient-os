import pytest
from brain.missions.mission_scheduler import MissionScheduler
from brain.routines.routine import Routine
from brain.load.load_model import LoadLevel
from brain.reflection.reflection_prompt import PromptType

def test_scheduler_reflection_hook():
    ms = MissionScheduler()
    
    # 1. Setup a heavy load schedule (many routines)
    # 20 routines * 10 score = 200 > 80 (High)
    for i in range(20):
        r = Routine(f"Task {i}", 32400, 1800, [])
        ms.routine_approval.add_candidate(r)
        ms.routine_approval.protect_routine(r.routine_id)
        
    # 2. Check Triggers
    # We need >= 2 days of high load for the Load Trigger.
    # get_load_snapshot generates 7 days based on Protected Routines.
    # Since routines apply to all days (empty days list), all 7 days will be HIGH.
    
    prompt = ms.check_reflection_triggers()
    
    assert prompt is not None
    assert prompt.type == PromptType.LOAD
    assert ms.active_reflection_prompt == prompt
