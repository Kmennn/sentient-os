import pytest
from brain.intents.intent import Intent
from brain.intents.conflict_detector import ConflictDetector
from brain.auth.role import UserRole

def test_resource_conflict():
    detector = ConflictDetector()
    
    active = Intent(user_id="u1", role=UserRole.OPERATOR, description="Watching", resources=["camera"])
    new = Intent(user_id="u2", role=UserRole.OPERATOR, description="Recording", resources=["camera", "mic"])
    
    conflicts = detector.check_conflicts(new, [active])
    
    assert len(conflicts) == 1
    assert conflicts[0].reason == "Resource Contention"
    assert "camera" in conflicts[0].resources_involved

def test_no_conflict():
    detector = ConflictDetector()
    active = Intent(user_id="u1", role=UserRole.OPERATOR, description="A", resources=["arm"])
    new = Intent(user_id="u2", role=UserRole.OPERATOR, description="B", resources=["leg"])
    
    assert len(detector.check_conflicts(new, [active])) == 0

def test_time_conflict():
    detector = ConflictDetector()
    
    # 100-200
    active = Intent(user_id="u1", role=UserRole.OPERATOR, description="A", time_window=(100, 200))
    
    # 150-250 (Overlap)
    new_overlap = Intent(user_id="u2", role=UserRole.OPERATOR, description="B", time_window=(150, 250))
    
    # 200-300 (Touch but no overlap usually, depends on strictly < or <=. Implementation uses < min(end))
    # max(100, 200) < min(200, 300) -> 200 < 200 -> False. Clean boundary.
    new_clean = Intent(user_id="u2", role=UserRole.OPERATOR, description="C", time_window=(200, 300))
    
    assert len(detector.check_conflicts(new_overlap, [active])) == 1
    assert len(detector.check_conflicts(new_clean, [active])) == 0
