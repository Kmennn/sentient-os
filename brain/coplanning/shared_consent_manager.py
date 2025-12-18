from brain.coplanning.shared_coplan import SharedCoPlanProposal

class SharedConsentManager:
    """
    Manages voting, quorum, and veto logic for shared proposals.
    """
    
    def register_vote(self, proposal: SharedCoPlanProposal, user_id: str, approved: bool):
        if proposal.vetoed:
            return # Already dead
            
        if not approved:
            proposal.vetoed = True
            proposal.approvals[user_id] = False
        else:
            proposal.approvals[user_id] = True
            
    def check_quorum(self, proposal: SharedCoPlanProposal) -> bool:
        if proposal.vetoed:
            return False
            
        # Check if all required approvers have approved
        for approver in proposal.required_approvers:
            if not proposal.approvals.get(approver, False):
                return False
                
        return True
    
    def override_veto(self, proposal: SharedCoPlanProposal, reason: str):
        """
        Allows Owner to override a veto or force approval.
        """
        proposal.vetoed = False
        proposal.override_reason = reason
        # Force all approvals to True? Or just bypass quorum check?
        # Usually override means "Execute it".
        # For simplicity, we assume override triggers execution flow elsewhere,
        # but here we ensure state reflects it's not vetoed.
        pass
