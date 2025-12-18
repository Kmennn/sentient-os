from brain.coplanning.coplan_proposal import CoPlanProposal, ProposalStatus
from brain.simulation.what_if_scenario import ChangeType

class CoPlanApplier:
    """
    Executes and reverts proposals on the Scheduler.
    """
    
    def apply(self, proposal: CoPlanProposal, scheduler):
        if proposal.status != ProposalStatus.PENDING:
            return False
            
        scenario = proposal.scenario
        
        if scenario.change_type == ChangeType.MOVE_TASK:
            # Find Routine and Update
            # Scheduler has `routine_approval`.
            # Note: We are modifying Protected Routines in memory.
            
            # 1. Find Routine
            routines = scheduler.routine_approval.get_protected_routines()
            routine = next((r for r in routines if r.routine_id == scenario.target_item_id), None)
            
            if routine:
                # 2. Store Undo Data
                proposal.undo_data = {
                    "time_of_day_seconds": routine.time_of_day_seconds
                }
                
                # 3. Apply
                if scenario.new_start_seconds is not None:
                    routine.time_of_day_seconds = scenario.new_start_seconds
                    proposal.status = ProposalStatus.APPLIED
                    return True
                    
        return False

    def revert(self, proposal: CoPlanProposal, scheduler):
        if proposal.status != ProposalStatus.APPLIED:
            return False
            
        scenario = proposal.scenario
        
        if scenario.change_type == ChangeType.MOVE_TASK:
             routines = scheduler.routine_approval.get_protected_routines()
             routine = next((r for r in routines if r.routine_id == scenario.target_item_id), None)
             
             if routine and proposal.undo_data:
                 routine.time_of_day_seconds = proposal.undo_data["time_of_day_seconds"]
                 proposal.status = ProposalStatus.REVERTED
                 return True
                 
        return False
