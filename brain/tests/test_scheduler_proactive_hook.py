import pytest
import time
import datetime
import inspect
from brain.missions.mission_scheduler import MissionScheduler
from brain.routines.routine import Routine

def test_scheduler_triggers_suggestion_deterministic():
    print(f"DEBUG SIG: {inspect.signature(MissionScheduler.tick)}")
    print(f"DEBUG FILE: {inspect.getfile(MissionScheduler)}")
    ms = MissionScheduler()
    
    # 1. Define a fixed time (e.g. today at 10:00:00 local)
    # Actually just use a timestamp that represents a known local time approach
    # logic in Suggester uses integer seconds from midnight.
    
    now = time.time()
    dt = datetime.datetime.fromtimestamp(now)
    midnight = datetime.datetime(dt.year, dt.month, dt.day).timestamp()
    
    # Let's say "now" is exactly 12:00:00 today
    # Construct timestamp for 12:00:00 today
    ts_noon = midnight + 12 * 3600
    
    # Target routine time = noon + 15m (900s) = 12:15:00
    # 12:00 = 43200s from midnight
    # 12:15 = 44100s from midnight
    
    r = Routine("Focus Mode", 44100, 1800, []) 
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    assert len(ms.routine_approval.get_protected_routines()) == 1
    
    # Tick with exact noon timestamp
    ms.tick(override_now=ts_noon)
    
    # Should trigger
    assert len(ms.pending_suggestions) == 1
    assert ms.pending_suggestions[0].name == "Focus Mode"
    
def test_scheduler_guard_prevents_double_trigger():
    ms = MissionScheduler()
    
    # Same setup
    now = time.time()
    dt = datetime.datetime.fromtimestamp(now)
    midnight = datetime.datetime(dt.year, dt.month, dt.day).timestamp()
    ts_noon = midnight + 12 * 3600
    r = Routine("Double", 44100, 60, [])
    
    ms.routine_approval.add_candidate(r)
    ms.routine_approval.protect_routine(r.routine_id)
    
    # 1st Tick
    ms.tick(override_now=ts_noon)
    assert len(ms.pending_suggestions) == 1
    
    # 2nd Tick (same time or slightly later)
    ms.tick(override_now=ts_noon + 1)
    assert len(ms.pending_suggestions) == 1 # Still 1
