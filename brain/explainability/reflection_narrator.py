from brain.reflection.reflection_prompt import ReflectionPrompt, PromptType

class ReflectionNarrator:
    """
    Generates strictly neutral reflection questions.
    """
    
    def narrate(self, prompt: ReflectionPrompt) -> str:
        # Constraint: No 'should', 'improve', 'optimize'.
        
        base = prompt.pattern_description
        
        if prompt.type == PromptType.LOAD:
            return f"{base} Would you like to reflect on your schedule balance?"
            
        if prompt.type == PromptType.CONFLICT:
            return f"{base} These recurring overlaps might be worth reviewing."
            
        return f"{base} Is this pattern working for you?"
