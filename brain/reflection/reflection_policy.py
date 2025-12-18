from brain.reflection.reflection_prompt import ReflectionPrompt

class ReflectionPolicy:
    """
    Determines if reflection prompts should be shown based on Trust.
    """
    
    def can_show_prompt(self, prompt: ReflectionPrompt, trust_score: float) -> bool:
        # Low trust: Never intrude with prompts.
        if trust_score < 0.4:
            return False
            
        # Medium trust (0.4 - 0.7): Only high confidence
        if trust_score < 0.7:
             return prompt.confidence > 0.85
             
        # High trust: Allow gentle prompts (all triggered ones are usually confident enough)
        return True
