
import pytest
import numpy as np
from brain.vision.depth_model_loader import DepthModelLoader

def test_loader_init():
    dl = DepthModelLoader()
    assert dl is not None

def test_inference_shape():
    dl = DepthModelLoader()
    # Create dummy frame
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    depth = dl.infer_depth(frame)
    
    assert depth.shape == (240, 320)
    assert np.all(depth >= 0.0)
    assert np.all(depth <= 1.0)
