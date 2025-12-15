
import pytest
from brain.explainability.hybrid_narrator import HybridNarrator
from brain.telemetry.hybrid_timeline import HybridTimeline

def test_narrative_generation():
    tl = HybridTimeline()
    tl.add_event("ALPHA_CHANGE", "Alpha=0.5")
    tl.add_event("POLICY", "Lift +0.1m")
    
    narrator = HybridNarrator(timeline=tl)
    story = narrator.generate_narrative()
    
    assert "Control shifted" in story
    assert "Policy suggested" in story
