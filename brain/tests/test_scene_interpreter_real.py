
import pytest
from brain.perception.scene_interpreter_real import SceneInterpreterReal

def test_initialization():
    si = SceneInterpreterReal()
    # Should not crash, regardless of cv2 presence
    assert si is not None

def test_frame_capture():
    si = SceneInterpreterReal()
    frame = si.get_frame()
    assert frame is not None

def test_process_live():
    si = SceneInterpreterReal()
    events = si.process_live_frame()
    # Expect at least one event (brightness) from mock or real
    assert isinstance(events, list)
    if si.is_mock:
        assert len(events) >= 1
    # If real, it depends on lighting, but shouldn't crash
