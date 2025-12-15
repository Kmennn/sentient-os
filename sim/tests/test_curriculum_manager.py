
import pytest
from sim.rl.curriculum_manager import CurriculumManager

def test_promotion():
    mgr = CurriculumManager()
    assert mgr.get_difficulty() == 0
    
    # 10 Successes
    for _ in range(10):
        mgr.record_success(True)
        
    assert mgr.get_difficulty() == 1
    
def test_no_promotion_if_failing():
    mgr = CurriculumManager()
    
    # 5 Success, 5 Fail
    for _ in range(5): mgr.record_success(True)
    for _ in range(5): mgr.record_success(False)
    
    assert mgr.get_difficulty() == 0
