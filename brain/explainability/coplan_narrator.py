from brain.coplanning.coplan_proposal import CoPlanProposal, ProposalStatus

class CoPlanNarrator:
    """
    Generates neutral status and consent messages for proposals.
    """
    
    def narrate(self, proposal: CoPlanProposal) -> str:
        if proposal.status == ProposalStatus.PENDING:
            return "Simulated changes ready. Waiting for approval."
            
        if proposal.status == ProposalStatus.APPLIED:
            return "Changes applied. You can undo this action."
            
        if proposal.status == ProposalStatus.REVERTED:
            return "Changes reverted. Schedule restored."
            
        return "Proposal status unknown."
