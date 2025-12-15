
import pytest
from brain.safety.execution_supervisor import ExecutionSupervisor
from brain.learning.confidence_monitor import ConfidenceMonitor

def test_supervisor_allow():
    mon = ConfidenceMonitor()
    sup = ExecutionSupervisor(monitor=mon)
    
    # Stable, Low Speed
    assert sup.supervise(current_speed=1.0)

def test_supervisor_speed_abort():
    sup = ExecutionSupervisor()
    assert not sup.supervise(current_speed=3.0) 

def test_supervisor_instability_abort():
    mon = ConfidenceMonitor()
    # Force instability
    mon.variance_threshold = 0.0
    mon.record_observation(1.0)
    mon.record_observation(2.0)
    
    sup = ExecutionSupervisor(monitor=mon)
    assert not sup.supervise(current_speed=1.0)
