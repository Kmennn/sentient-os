from brain.coplanning.shared_coplan import SharedCoPlanProposal

class SharedCoPlanNarrator:
    """
    Generates status messages for multi-user proposals.
    """
    
    def narrate_status(self, proposal: SharedCoPlanProposal) -> str:
        if proposal.vetoed:
            if proposal.override_reason:
                return f"Veto overridden: {proposal.override_reason}"
            return "Change vetoed. Execution paused."
            
        # Count approvals
        approved_count = sum(1 for v in proposal.approvals.values() if v)
        total_required = len(proposal.required_approvers)
        
        if approved_count >= total_required:
            return "All approvals received. Ready to execute."
            
        return f"Waiting for approval ({approved_count}/{total_required})."
