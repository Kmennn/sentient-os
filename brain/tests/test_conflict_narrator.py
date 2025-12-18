import pytest
from brain.explainability.conflict_narrator import ConflictNarrator
from brain.intents.conflict_detector import ConflictReport
from brain.intents.intent import Intent
from brain.auth.role import UserRole

def test_narrator_output():
    narrator = ConflictNarrator()
    
    new = Intent(user_id="u1", role=UserRole.OPERATOR, description="New Mission", resources=["arm"])
    active = Intent(user_id="u2", role=UserRole.OWNER, description="Active Mission", resources=["arm"])
    
    report = ConflictReport(
        new_intent=new,
        active_intent=active,
        reason="Resource Contention",
        resources_involved=["arm"]
    )
    
    desc = narrator.describe(report)
    
    assert "Conflict detected" in desc
    assert "New Mission" in desc
    assert "OPERATOR" in desc
    assert "Active Mission" in desc
    assert "OWNER" in desc
    assert "Resource Contention" in desc
    assert "arm" in desc
