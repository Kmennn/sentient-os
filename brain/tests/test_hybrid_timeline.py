
import pytest
from brain.telemetry.hybrid_timeline import HybridTimeline

def test_timeline_recording():
    tl = HybridTimeline()
    tl.add_event("ALPHA_CHANGE", "Alpha ramped to 0.5")
    
    events = tl.get_events()
    assert len(events) == 1
    assert events[0]["type"] == "ALPHA_CHANGE"
    assert "timestamp" in events[0]
