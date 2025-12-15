
import pytest
from brain.affordances.affordance_engine import AffordanceEngine
from brain.vision.object_semantics import SemanticObject, SemanticProperties

def test_affordance_lookup():
    eng = AffordanceEngine()
    
    # Cup
    cup = SemanticObject("1", "cup", "vessel", {"x":0,"y":0,"z":0})
    allowed = eng.get_affordances(cup)
    
    assert "grasp" in allowed
    assert "pour_into" in allowed
    assert "avoid" not in allowed

def test_electronics_restriction():
    eng = AffordanceEngine()
    
    # Laptop
    laptop = SemanticObject("2", "laptop", "electronics", {"x":0,"y":0,"z":0})
    
    assert eng.is_action_allowed(laptop, "avoid")
    assert not eng.is_action_allowed(laptop, "pour_into")
