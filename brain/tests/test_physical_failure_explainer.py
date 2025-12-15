
import pytest
from brain.explainability.physical_failure_explainer import PhysicalFailureExplainer

def test_explanation():
    explainer = PhysicalFailureExplainer()
    
    msg = explainer.explain("OCCLUSION", {"x": 1.0, "y": 0.5})
    assert "Path blocked" in msg
    assert "1.00" in msg
    
    msg2 = explainer.explain("AFFORDANCE_VIOLATION", {"action": "pour", "object_label": "laptop"})
    assert "pour" in msg2
    assert "laptop" in msg2
