import pytest
import time
from brain.missions.mission_scheduler import MissionScheduler, MissionPriority
from brain.missions.mission_contract import MissionContract
from brain.auth.role import UserRole
from brain.preferences.scheduling_preferences import SchedulingPreferences, DelayTolerance

def test_scheduler_low_tolerance_rejects():
    ms = MissionScheduler()
    
    # 1. Set Prefs to LOW
    prefs = SchedulingPreferences(user_id="u1", delay_tolerance=DelayTolerance.LOW)
    ms.set_user_preferences(prefs)
    
    # 2. Start Active Mission
    c1 = MissionContract(created_by="owner", execution_role=UserRole.OWNER, allowed_objects=["res"])
    ms.schedule("m1", MissionPriority.USER, payload=c1)
    ms.tick()
    
    # 3. Schedule Conflicting Mission by User u1
    c2 = MissionContract(created_by="u1", execution_role=UserRole.OPERATOR, allowed_objects=["res"])
    
    # Normally Flexible -> Delay (5m). But LOW tolerance > 1m delay -> Expiration.
    res = ms.schedule("m2", MissionPriority.USER, payload=c2)
    
    assert res == "REJECTED"

def test_scheduler_high_tolerance_accepts():
    ms = MissionScheduler()
    
    prefs = SchedulingPreferences(user_id="u1", delay_tolerance=DelayTolerance.HIGH)
    ms.set_user_preferences(prefs)
    
    c1 = MissionContract(created_by="owner", execution_role=UserRole.OWNER, allowed_objects=["res"])
    ms.schedule("m1", MissionPriority.USER, payload=c1)
    ms.tick()
    
    c2 = MissionContract(created_by="u1", execution_role=UserRole.OPERATOR, allowed_objects=["res"])
    
    # Flexible -> Delay. HIGH tolerance accepts it.
    ms.schedule("m2", MissionPriority.USER, payload=c2)
    
    assert len(ms._queue) == 1
    assert ms._queue[0].blocked_until > time.time()
