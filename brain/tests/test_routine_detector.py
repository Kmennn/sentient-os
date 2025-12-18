import pytest
from brain.routines.routine import Routine
from brain.routines.routine_detector import RoutineDetector

def test_routine_time_matching():
    # 9:00 AM = 9*3600 = 32400
    r = Routine("Test", 32400, 3600, [0,1,2])
    
    # 9:10 AM matches
    assert r.matches_time(32400 + 600)
    
    # 10:00 AM (3600s later) - tolerance default 1800 (30m) -> No match
    assert not r.matches_time(32400 + 3600)

def test_detector_finds_cluster():
    detector = RoutineDetector()
    
    # 3 logins around 9:00 AM (32400)
    history = [
        {"name": "Login", "start_time_of_day": 32400, "duration": 60},
        {"name": "Login", "start_time_of_day": 32500, "duration": 60},
        {"name": "Login", "start_time_of_day": 32300, "duration": 60},
        {"name": "Random", "start_time_of_day": 50000, "duration": 60},
    ]
    
    candidates = detector.detect_candidates(history)
    assert len(candidates) == 1
    c = candidates[0]
    assert c.name == "Login"
    assert 32300 < c.time_of_day_seconds < 32500
    assert c.confidence > 0.5

def test_detector_ignores_scattered():
    detector = RoutineDetector()
    history = [
        {"name": "Scatter", "start_time_of_day": 10000, "duration": 60},
        {"name": "Scatter", "start_time_of_day": 50000, "duration": 60},
        {"name": "Scatter", "start_time_of_day": 80000, "duration": 60},
    ]
    candidates = detector.detect_candidates(history)
    assert len(candidates) == 0
