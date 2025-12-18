import pytest
from brain.explainability.reflection_narrator import ReflectionNarrator
from brain.reflection.reflection_policy import ReflectionPolicy
from brain.reflection.reflection_prompt import ReflectionPrompt, PromptType

def test_narrator_neutrality():
    narrator = ReflectionNarrator()
    pro = ReflectionPrompt("id", PromptType.LOAD, "High activity detected.", 0.9)
    
    text = narrator.narrate(pro)
    
    forbidden = ["should", "improve", "optimize", "better"]
    for word in forbidden:
        assert word not in text.lower()
        
    assert "reflect" in text.lower() or "review" in text.lower()

def test_policy_trust_gates():
    policy = ReflectionPolicy()
    pro = ReflectionPrompt("id", PromptType.LOAD, "High load", 0.9)
    
    # Low trust -> Block
    assert policy.can_show_prompt(pro, 0.2) is False
    
    # Med trust -> Allow high conf
    assert policy.can_show_prompt(pro, 0.5) is True
    
    # Med trust -> Block low conf
    low_conf = ReflectionPrompt("id", PromptType.LOAD, "Maybe", 0.5)
    assert policy.can_show_prompt(low_conf, 0.5) is False
