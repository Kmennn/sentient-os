from brain.load.load_model import LoadLevel

class LoadPolicy:
    """
    Determines visibility of load insights.
    """
    
    def should_show_insight(self, level: LoadLevel, trust_score: float) -> bool:
        # Low trust: Only show HIGH load (critical info).
        if trust_score < 0.3:
            return level == LoadLevel.HIGH
            
        # Normal trust: Show all
        return True
