import pytest
import time
from brain.proactive.suggestion_guard import SuggestionGuard
from brain.proactive.routine_suggester import RoutineSuggester
from brain.routines.routine import Routine

def test_guard_daily_limit():
    guard = SuggestionGuard()
    rid = "r1"
    t = time.time()
    
    assert guard.check_guard(rid, t)
    guard.record_suggestion(rid, t)
    
    assert not guard.check_guard(rid, t + 60) # Same day, limit 1

def test_guard_suppression():
    guard = SuggestionGuard()
    rid = "r2"
    
    # Reject 1
    guard.record_rejection(rid)
    assert guard.check_guard(rid, 0)
    
    # Reject 2
    guard.record_rejection(rid)
    assert not guard.check_guard(rid, 0) # Suppressed

def test_suggester_timing():
    guard = SuggestionGuard()
    suggester = RoutineSuggester(guard)
    
    # Routine at 9:00 AM (32400s)
    r = Routine("Morning", 32400, 60, [])
    
    # Current time: 8:45 AM (31500s)
    # Target: 9:00 AM. 
    # Suggester looks ahead 900s (15m). So if now is 31500, lookahead is 32400. Match!
    
    # Mock time.time() via argument to check_suggestions
    # Need to construct a timestamp where local time is 8:45 AM
    # This is tricky with timezones/local. 
    # Let's bypass by hacking routine time relative to "now".
    
    now = time.time()
    dt = datetime.datetime.fromtimestamp(now)
    midnight = datetime.datetime(dt.year, dt.month, dt.day).timestamp()
    secs_now = now - midnight
    
    # Routine starts in 15 mins
    r.time_of_day_seconds = int(secs_now + 900)
    
    res = suggester.check_suggestions(now, [r])
    assert res == r
    
    # Next check should be blocked by guard
    res2 = suggester.check_suggestions(now + 10, [r])
    assert res2 is None
    
import datetime
