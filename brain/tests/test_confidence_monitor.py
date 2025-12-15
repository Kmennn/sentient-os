
import pytest
from brain.learning.confidence_monitor import ConfidenceMonitor

def test_stability_check():
    mon = ConfidenceMonitor()
    # Consistent low variance
    for _ in range(5):
        mon.record_observation(0.1)
        
    assert mon.is_stable()

def test_instability_detection():
    mon = ConfidenceMonitor()
    mon.variance_threshold = 0.01 # Strict
    
    # High variance input: 0.1, 0.9, 0.1, 0.9
    mon.record_observation(0.1)
    mon.record_observation(0.9)
    mon.record_observation(0.1)
    mon.record_observation(0.9)
    
    # Mean 0.5. Var approx 0.16. > 0.01
    assert not mon.is_stable()
