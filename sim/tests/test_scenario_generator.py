
import pytest
from sim.envs.scenario_generator import ScenarioGenerator

def test_difficulty_levels():
    gen = ScenarioGenerator()
    
    # Level 0
    _, obs0, _ = gen.generate(difficulty=0, seed=42)
    assert len(obs0) == 0
    
    # Level 1
    _, obs1, _ = gen.generate(difficulty=1, seed=42)
    assert len(obs1) == 1
    
    # Level 2
    _, obs2, _ = gen.generate(difficulty=2, seed=42)
    assert len(obs2) >= 3 # 1 (from lvl 1 logic if stacked?) No, logic is separate ifs.
    # Logic: if >=1 add 1. if >=2 add 2 more. Total 3.
    assert len(obs2) == 3

def test_determinism():
    gen = ScenarioGenerator()
    t1, o1, _ = gen.generate(1, seed=123)
    t2, o2, _ = gen.generate(1, seed=123)
    
    assert t1 == t2
    assert o1 == o2
