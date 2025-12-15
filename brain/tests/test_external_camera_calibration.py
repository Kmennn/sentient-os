
import pytest
import numpy as np
import os
from brain.robotics.calibration.external_camera_calibration import CalibrationEngine

def test_intrinsics_mock():
    # Even without CV2, this should pass via Mock
    ce = CalibrationEngine(calibration_file="data/test_calib.json")
    ce.force_mock()
    
    # Fake data
    obj_pts = [np.zeros((6*7, 3), np.float32)]
    img_pts = [np.zeros((6*7, 2), np.float32)]
    
    err = ce.calibrate_intrinsics(img_pts, obj_pts, (640, 480))
    assert err >= 0.0
    assert ce.is_calibrated

def test_extrinsics_mock():
    ce = CalibrationEngine(calibration_file="data/test_calib.json")
    ce.force_mock()
    # Force intrinsics
    ce.camera_matrix = np.eye(3)
    ce.dist_coeffs = np.zeros(5)
    
    world_pts = np.array([
        [0,0,0], [1,0,0], [0,1,0], [0,0,1],
        [1,1,0], [0,1,1]
    ], dtype=np.float32)
    img_pts = np.array([
        [0,0], [10,0], [0,10], [5,5],
        [10,10], [5,10]
    ], dtype=np.float32)
    
    success = ce.compute_extrinsics(img_pts, world_pts)
    assert success

def test_save_load():
    ce = CalibrationEngine(calibration_file="data/test_calib.json")
    ce.camera_matrix = np.eye(3)
    ce.rotation_vec = np.zeros((3,1))
    
    ce.save_profile()
    assert os.path.exists("data/test_calib.json")
    
    ce2 = CalibrationEngine(calibration_file="data/test_calib.json")
    assert ce2.is_calibrated
    assert np.array_equal(ce2.camera_matrix, ce.camera_matrix)
