
import pytest
from core.vision.detect_engine import detect_engine

def test_detect_heuristics():
    # Test Window Classification
    assert detect_engine._classify_window("Google Chrome") == "Browser"
    assert detect_engine._classify_window("VS Code") == "IDE"
    assert detect_engine._classify_window("Notepad") == "UnknownApp"

def test_detect_flow():
    # Mock metadata
    metadata = {
        "active_window": "Slack - General",
        "source": "monitor_1"
    }
    # Image data irrelevant for heuristics (stubbed logic)
    res = detect_engine.detect(b'fake_image', metadata)
    
    assert "App:ChatApp" in res["objects"]
    assert res["confidence"] > 0.0
