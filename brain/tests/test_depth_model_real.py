
import pytest
import numpy as np
from brain.vision.depth_model import DepthModel

def test_depth_init():
    dm = DepthModel()
    assert dm is not None

def test_inference_mock():
    dm = DepthModel()
    # Mock frame
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    depth = dm.infer(frame)
    
    assert depth.shape == (100, 100)
    assert np.max(depth) <= 1.0
    assert np.min(depth) >= 0.0
    
    # Verify "object" blob in center (should be 0.8)
    assert depth[50, 50] == 0.8
