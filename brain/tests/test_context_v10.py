
import pytest
from brain.context.context_v10 import ContextManagerV10
from brain.embodiment.motion_model import motion_model

@pytest.fixture
def ctx():
    return ContextManagerV10(persistence_path="data/test_context_v10.json")

def test_hardware_integration(ctx):
    motion_model.update((0, 15, 5), (0,0,0)) # Moving
    
    snap = ctx.get_hardware_snapshot({}, [])
    
    assert snap["motion"]["state"] == "MOVING"
    assert "audio_level" in snap
    assert "robot" in snap
    assert snap["robot"]["gripper"] == "OPEN"
