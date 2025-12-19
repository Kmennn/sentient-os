from dataclasses import dataclass

@dataclass
class AutonomyBudget:
    window_seconds: int = 86400 # 24 Hours
    max_actions: int = 50
    max_failures: int = 5
    max_rollbacks: int = 3
    
@dataclass
class BudgetUsage:
    actions_count: int
    failures_count: int
    rollbacks_count: int
    window_start: float
    is_blocked: bool
    block_reason: str = ""
