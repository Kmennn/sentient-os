
import pytest
from sim.rl.distillation import KnowledgeDistiller
from sim.rl.policy_trainer import SimplePolicy

def test_distillation_structure():
    distiller = KnowledgeDistiller()
    policy = SimplePolicy()
    
    rules = distiller.distill(policy, episodes=5)
    
    assert "suggested_safe_height" in rules
    assert isinstance(rules["suggested_safe_height"], float)
