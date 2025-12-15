
import pytest
from brain.explainability.blend_trace import BlendTrace, BlendTraceRecord

def test_trace_formatting():
    trace = BlendTrace()
    rec = BlendTraceRecord(
        parameter="lift",
        base_value=0.05,
        policy_delta=0.2,
        alpha=0.5,
        final_value=0.15
    )
    
    msg = trace.generate_trace(rec)
    assert "Planner(0.05)" in msg
    assert "Policy(+0.20 * 50%)" in msg
    assert "Final(0.15)" in msg
