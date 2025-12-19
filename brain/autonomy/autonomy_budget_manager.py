import time
from typing import List
from brain.autonomy.autonomy_budget import AutonomyBudget, BudgetUsage
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType

class AutonomyBudgetManager:
    def __init__(self, ledger: AutonomyLedger):
        self.ledger = ledger
        self.base_budget = AutonomyBudget()

    def get_usage(self, trust_score: float) -> BudgetUsage:
        now = time.time()
        window_start = now - self.base_budget.window_seconds
        
        entries = self.ledger.get_entries()
        # Filter for window
        recent_entries = [e for e in entries if e.timestamp >= window_start]
        
        # Count
        actions = 0
        failures = 0
        rollbacks = 0
        
        for e in recent_entries:
            if e.decision_type == DecisionType.ACTION_EXECUTED:
                actions += 1
            elif e.decision_type == DecisionType.ACTION_ROLLBACK_EXECUTED:
                rollbacks += 1
            
            # Use reason or type to detect failure? 
            # In v20.1 we record ACTION_RESULT_RECORDED with failure status, OR we might rely on specific types.
            # Let's count ACTION_RESULT_RECORDED where log text says Failed or check associated logic.
            # Actually, simplest is to check the textual reason or just rely on a new explicit FAIL event if I added one.
            # v20.1 added ACTION_RESULT_RECORDED, but the Decision object stores string reason.
            # I'll rely on checking `ACTION_ROLLBACK_FAILED` and maybe assume failures are logged as BLOCKED?
            # Wait, `record_action_outcome` in scheduler updates trust but doesn't explicitly log a "FAILURE" event type to ledger (it prints).
            # The executor logs `ACTION_BLOCKED` on failure/error.
            # Let's count `ACTION_BLOCKED` as a failure usage? Or maybe `ACTION_BLOCKED` is pre-execution block?
            # Executor logs `ACTION_BLOCKED` on runtime error too.
            # Let's count `ACTION_BLOCKED` (runtime errors) as failures.
            if e.decision_type == DecisionType.ACTION_BLOCKED and "Runtime Error" in (e.reason or ""):
                failures += 1
            if e.decision_type == DecisionType.ACTION_ROLLBACK_FAILED:
                failures += 1
                
        # Adjust Limits by Trust
        adjusted_actions = self.base_budget.max_actions
        adjusted_failures = self.base_budget.max_failures
        
        if trust_score > 0.8:
            adjusted_actions = int(adjusted_actions * 1.5)
            adjusted_failures = int(adjusted_failures * 1.2)
        elif trust_score < 0.4:
            adjusted_actions = int(adjusted_actions * 0.2)
            adjusted_failures = 1 # Very strict
            
        usage = BudgetUsage(
            actions_count=actions,
            failures_count=failures,
            rollbacks_count=rollbacks,
            window_start=window_start,
            is_blocked=False
        )
        
        if actions >= adjusted_actions:
            usage.is_blocked = True
            usage.block_reason = f"Action Budget Exceeded ({actions}/{adjusted_actions})"
        elif failures >= adjusted_failures:
            usage.is_blocked = True
            usage.block_reason = f"Failure Budget Exceeded ({failures}/{adjusted_failures})"
        elif rollbacks >= self.base_budget.max_rollbacks:
            usage.is_blocked = True
            usage.block_reason = f"Rollback Budget Exceeded ({rollbacks}/{self.base_budget.max_rollbacks})"
            
        return usage
        
    def check_allowance(self, trust_score: float) -> bool:
        usage = self.get_usage(trust_score)
        return not usage.is_blocked
