
import pytest
import numpy as np
from brain.vision.depth_estimator import DepthEstimator

def test_depth_output():
    de = DepthEstimator()
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    depth = de.estimate_depth(frame)
    assert depth is not None
    assert depth.shape == (100, 100)
    assert np.all(depth >= 0.0)
    assert np.all(depth <= 1.0)
    
    # Check gradient (top row < bottom row)
    assert depth[0, 50] < depth[99, 50]

def test_mock_input():
    de = DepthEstimator()
    depth = de.estimate_depth({"mock": True})
    assert depth is not None
