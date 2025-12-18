import pytest
from brain.explainability.routine_narrator import RoutineNarrator
from brain.routines.routine import Routine

def test_explain_conflict():
    narrator = RoutineNarrator()
    r = Routine("Focus", 0, 0, [])
    msg = narrator.explain_routine_conflict("Game", r)
    assert "deferred" in msg
    assert "Focus" in msg

def test_explain_candidate():
    narrator = RoutineNarrator()
    r = Routine("Login", 0, 0, [], confidence=0.85)
    msg = narrator.explain_candidate(r)
    assert "85%" in msg
    assert "Login" in msg
