from brain.coplanning.coplan_proposal import CoPlanProposal

class ConsentManager:
    """
    Validates if a proposal can be applied based on user trust and explicit consent rules.
    """
    
    def request_consent(self, proposal: CoPlanProposal, trust_score: float) -> bool:
        # Default policy: Explicit consent is ALWAYS required for changes.
        # This function exists to gate automation if we ever added it, 
        # or to flagging if "Double Confirmation" is needed in UI.
        
        # Low trust -> Strictly manual, maybe extra warnings (handled in UI via flags)
        # return True simply means "Change is valid to prompt for"
        
        if trust_score < 0.2:
            # Maybe block complex changes?
            pass
            
        return True # In v6.0, all proposals require explicit user action, so we just allow the flow.
