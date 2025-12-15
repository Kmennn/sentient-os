
import pytest
from brain.tasks.dag_runtime import DAGRuntime, DAGNode, NodeStatus

def test_linear_dependency():
    runtime = DAGRuntime()
    nodes = [
        DAGNode(node_id="A", action="open", object_id="door"),
        DAGNode(node_id="B", action="enter", object_id="room", dependencies=["A"])
    ]
    runtime.load_graph(nodes)
    
    # Only A should be ready
    ready = runtime.get_ready_nodes()
    assert len(ready) == 1
    assert ready[0].node_id == "A"
    
    # Complete A
    runtime.complete_node("A")
    
    # Now B should be ready
    ready = runtime.get_ready_nodes()
    assert len(ready) == 1
    assert ready[0].node_id == "B"

def test_branching():
    # A -> B, A -> C, B+C -> D
    runtime = DAGRuntime()
    nodes = [
        DAGNode(node_id="A", action="root", object_id="x"),
        DAGNode(node_id="B", action="branch1", object_id="x", dependencies=["A"]),
        DAGNode(node_id="C", action="branch2", object_id="x", dependencies=["A"]),
        DAGNode(node_id="D", action="merge", object_id="x", dependencies=["B", "C"])
    ]
    runtime.load_graph(nodes)
    
    runtime.complete_node("A")
    ready = runtime.get_ready_nodes()
    assert len(ready) == 2 # B and C
    node_ids = sorted([n.node_id for n in ready])
    assert node_ids == ["B", "C"]
    
    # Complete B only
    runtime.complete_node("B")
    # D not ready yet (C pending)
    ready = runtime.get_ready_nodes()
    assert len(ready) == 1
    assert ready[0].node_id == "C"
    
    # Complete C
    runtime.complete_node("C")
    ready = runtime.get_ready_nodes()
    assert len(ready) == 1
    assert ready[0].node_id == "D"
