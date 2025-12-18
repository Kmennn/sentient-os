from brain.week.week_plan import WeeklyPattern

class WeekPolicy:
    """
    Determines which insights to show.
    """
    
    def should_show_insight(self, pattern: WeeklyPattern, trust_score: float) -> bool:
        # Low trust: Only show very high confidence (> 0.9)
        if trust_score < 0.3:
            return pattern.confidence > 0.9

        # High confidence patterns always shown otherwise
        if pattern.confidence > 0.8:
            return True

        return True
