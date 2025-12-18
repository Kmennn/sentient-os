import uuid
from brain.simulation.what_if_scenario import WhatIfScenario
from brain.coplanning.coplan_proposal import CoPlanProposal, ProposalStatus

class CoPlanEngine:
    """
    Manages creation and lifecycle of proposals.
    """
    
    def create_proposal(self, scenario: WhatIfScenario) -> CoPlanProposal:
        return CoPlanProposal(
            proposal_id=str(uuid.uuid4()),
            scenario=scenario,
            status=ProposalStatus.PENDING
        )
