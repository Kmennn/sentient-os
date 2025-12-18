from brain.intents.conflict_detector import ConflictReport

class ConflictNarrator:
    """
    Generates human-readable explanations for conflicts.
    """
    
    def describe(self, report: ConflictReport) -> str:
        new = report.new_intent
        active = report.active_intent
        
        # Format: "Mission A paused: OPERATOR request conflicts with OWNER mission."
        # Or detailed: "Conflict: [New Desc] by [Role] vs [Active Desc] by [Role]. Reason: [Reason]."
        
        narrative = f"Conflict detected: '{new.description}' ({new.role.name}) " \
                    f"vs active '{active.description}' ({active.role.name}). " \
                    f"Reason: {report.reason}."
                    
        if report.resources_involved:
            res_str = ", ".join(report.resources_involved)
            narrative += f" Involved resources: [{res_str}]."
            
        return narrative
