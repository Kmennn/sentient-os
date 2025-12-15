
import pytest
from brain.skills.skill_confidence import SkillConfidenceManager

def test_success_boost():
    scm = SkillConfidenceManager()
    scm.record_execution("test", True)
    assert scm.scores["test"].score == 1.0

def test_decay_block():
    scm = SkillConfidenceManager()
    # 1 success, 4 fails. Score = 0.2
    scm.record_execution("bad_skill", True)
    for _ in range(4):
        scm.record_execution("bad_skill", False)
        
    assert scm.scores["bad_skill"].score == 0.2
    assert not scm.is_viable("bad_skill")
