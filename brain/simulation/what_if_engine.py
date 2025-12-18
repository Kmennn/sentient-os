import copy
from brain.day.day_plan import DayPlan, PlanItem
from brain.simulation.what_if_scenario import WhatIfScenario, ChangeType

class WhatIfEngine:
    """
    Applies scenarios to DayPlans to produce a simulated outcome.
    """
    
    def simulate(self, day_plan: DayPlan, scenario: WhatIfScenario) -> DayPlan:
        # 1. Deep copy
        simulated_plan = copy.deepcopy(day_plan)
        
        # 2. Find target item
        target_item = next((i for i in simulated_plan.items if i.id == scenario.target_item_id), None)
        
        if not target_item:
            return simulated_plan # Target not found, no change
            
        # 3. Apply Change
        if scenario.change_type == ChangeType.REMOVE_TASK:
            simulated_plan.items.remove(target_item)
            
        elif scenario.change_type == ChangeType.MOVE_TASK:
            if scenario.new_start_seconds is not None:
                target_item.start_seconds = scenario.new_start_seconds
                
        # 4. Re-calculate Conflicts
        # Clear existing warnings first? Or just append 'Simulated Conflict'?
        # For a clean simulation, we should re-assess.
        self._reassess_conflicts(simulated_plan)
        
        return simulated_plan

    def _reassess_conflicts(self, plan: DayPlan):
        # Reset warnings
        for item in plan.items:
            item.warnings = []
            
        # Simple overlap check
        # Sort by start time for easier checking
        sorted_items = sorted(plan.items, key=lambda x: x.start_seconds)
        
        for i in range(len(sorted_items)):
            current = sorted_items[i]
            current_end = current.start_seconds + current.duration_seconds
            
            for j in range(i + 1, len(sorted_items)):
                next_item = sorted_items[j]
                if next_item.start_seconds < current_end:
                    # Overlap
                    msg = f"Simulated Overlap with {next_item.name}"
                    current.warnings.append(msg)
                    next_item.warnings.append(f"Simulated Overlap with {current.name}")
                else:
                    break # Sorted, so no more overlaps possible for 'current'
