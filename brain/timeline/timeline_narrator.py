from brain.autonomy.autonomy_ledger import DecisionType, AutonomyDecision

class TimelineNarrator:
    @staticmethod
    def narrate(decision: AutonomyDecision) -> str:
        t = decision.decision_type
        r = decision.reason
        
        if t == DecisionType.ALERT_FILTERED_BY_PREFERENCE:
            return f"Filtered alert based on preference rules ({r})"
        elif t == DecisionType.ALERT_SHOWN_BY_PREFERENCE:
            return f"Allowed alert to show ({r})"
        elif t == DecisionType.USER_MEANING_UPDATED:
            return f"Learned new relevance for {r}"
        elif t == DecisionType.REFLECTION_NEGATIVE:
            return f"Reflected on potential mistake: {r}"
        elif t == DecisionType.REFLECTION_POSITIVE:
            return f"Confirmed correct behavior: {r}"
        elif t == DecisionType.ADJUSTMENT_PROPOSED:
            return f"Proposed adjustment: {r}"
        elif t == DecisionType.ADJUSTMENT_APPROVED:
            return f"Approved adjustment: {r}"
        elif t == DecisionType.SYNC_CONFLICT_RESOLVED:
            return f"Resolved sync conflict: {r}"
        elif t == DecisionType.AGENT_BOUNDARY_VIOLATION:
            return f"Blocked unauthorized agent action: {r}"
            
        return r or "System Event"
