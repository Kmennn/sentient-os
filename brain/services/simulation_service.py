from brain.simulation.what_if_engine import WhatIfEngine
from brain.simulation.what_if_scenario import WhatIfScenario
from brain.simulation.impact_comparator import ImpactComparator, ImpactReport
from brain.coplanning.coplan_engine import CoPlanEngine
from brain.coplanning.coplan_applier import CoPlanApplier
from brain.coplanning.coplan_proposal import CoPlanProposal
import datetime

class SimulationService:
    def __init__(self, day_planner, routine_approval):
        self.what_if_engine = WhatIfEngine()
        self.impact_comparator = ImpactComparator()
        self.coplan_engine = CoPlanEngine()
        self.coplan_applier = CoPlanApplier()
        self.day_planner = day_planner
        self.routine_approval = routine_approval

    def simulate_scenario(self, scenario: WhatIfScenario, queued_missions) -> ImpactReport:
        today = datetime.date.today()
        routines = list(self.routine_approval.get_protected_routines())
        queued = list(queued_missions)
        
        current_plan = self.day_planner.generate_plan(routines, queued, [], today)
        simulated_plan = self.what_if_engine.simulate(current_plan, scenario)
        return self.impact_comparator.compare(current_plan, simulated_plan)

    def create_proposal(self, scenario: WhatIfScenario) -> CoPlanProposal:
        return self.coplan_engine.create_proposal(scenario)

    def apply_proposal(self, proposal: CoPlanProposal, scheduler_ref) -> bool:
        return self.coplan_applier.apply(proposal, scheduler_ref)

    def undo_proposal(self, proposal: CoPlanProposal, scheduler_ref) -> bool:
        return self.coplan_applier.revert(proposal, scheduler_ref)
