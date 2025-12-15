
import pytest
from brain.runtime.resource_locks import ResourceLockManager

def test_acquisition():
    locks = ResourceLockManager()
    
    # Mission A acquires Arm
    assert locks.acquire("MissionA", "arm_left") is True
    assert locks.is_locked("arm_left") is True
    
    # Mission B tries -> Fail
    assert locks.acquire("MissionB", "arm_left") is False
    
    # Mission A re-acquires -> OK
    assert locks.acquire("MissionA", "arm_left") is True

def test_release():
    locks = ResourceLockManager()
    locks.acquire("MissionA", "camera")
    
    # Mission B tries release -> No effect (it doesn't own it)
    locks.release("MissionB", "camera")
    assert locks.is_locked("camera") is True
    
    # Mission A releases -> OK
    locks.release("MissionA", "camera")
    assert locks.is_locked("camera") is False
    
    # Mission B acquires -> OK now
    assert locks.acquire("MissionB", "camera") is True

def test_release_all():
    locks = ResourceLockManager()
    locks.acquire("MissionA", "r1")
    locks.acquire("MissionA", "r2")
    locks.acquire("MissionB", "r3")
    
    locks.release_all("MissionA")
    assert locks.is_locked("r1") is False
    assert locks.is_locked("r2") is False
    assert locks.is_locked("r3") is True # B still holds
