
import pytest
from brain.vision.object_semantics import ObjectRegistry, SemanticObject, SemanticProperties

def test_object_registry_flow():
    reg = ObjectRegistry()
    
    props = SemanticProperties(is_fragile=True)
    obj = SemanticObject(
        id="obj_123",
        label="wine_glass",
        class_type="glassware",
        position={"x":1, "y":2, "z":0},
        properties=props
    )
    
    reg.update_object(obj)
    
    retrieved = reg.get_object("obj_123")
    assert retrieved is not None
    assert retrieved.label == "wine_glass"
    assert retrieved.properties.is_fragile
    assert len(reg.list_objects()) == 1

def test_missing_object():
    reg = ObjectRegistry()
    assert reg.get_object("ghost") is None
