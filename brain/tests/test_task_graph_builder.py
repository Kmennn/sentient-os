
import pytest
from brain.tasks.task_graph_builder import TaskGraphBuilder

def test_pick_place_chain():
    builder = TaskGraphBuilder()
    chain = builder.build_chain("pick_and_place", "cup_1")
    
    assert len(chain) == 3
    assert chain[0].skill_name == "grasp"
    assert chain[0].next_nodes == ["step2"]
    assert chain[1].skill_name == "lift"
    assert chain[2].skill_name == "place"

def test_unknown_intent():
    builder = TaskGraphBuilder()
    chain = builder.build_chain("teleport", "cup_1")
    assert len(chain) == 0
