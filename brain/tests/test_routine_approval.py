import pytest
from brain.routines.routine_approval import RoutineApproval
from brain.routines.routine import Routine

def test_routine_lifecycle():
    mgr = RoutineApproval()
    r = Routine("Morning", 300, 60, [])
    
    mgr.add_candidate(r)
    assert r.routine_id in mgr.candidates
    assert len(mgr.protected) == 0
    
    # Protect
    mgr.protect_routine(r.routine_id)
    assert r.routine_id not in mgr.candidates
    assert r.routine_id in mgr.protected
    assert mgr.protected[r.routine_id].protected == True

def test_ignore_routine():
    mgr = RoutineApproval()
    r = Routine("Noise", 100, 10, [])
    
    mgr.add_candidate(r)
    mgr.ignore_routine(r.routine_id)
    
    assert r.routine_id not in mgr.candidates
    assert r.routine_id not in mgr.protected
    assert r.routine_id in mgr.ignored_ids
