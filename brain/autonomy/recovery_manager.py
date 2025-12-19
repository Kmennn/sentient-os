import time
from brain.autonomy.recovery_state import RecoveryState, RecoveryLevel, RecoveryTrigger
from brain.autonomy.autonomy_ledger import AutonomyLedger, AutonomyDecision, DecisionType
import uuid

class RecoveryManager:
    def __init__(self, ledger: AutonomyLedger):
        self.ledger = ledger
        self.state = RecoveryState()
        self.active_device_id = "unknown" # Will be set by scheduler

    def update_device_id(self, device_id: str):
        self.active_device_id = device_id

    def check_triggers(self):
        # Scan recent events logic could be here, or we can rely on explicit notification from Scheduler.
        # For budgeting, we rely on BudgetManager notifications (or Scheduler checking budget).
        # For failures, we scan ledger?
        # Let's rely on 'notify_event' pattern for now, but also can scan.
        pass

    def notify_failure(self):
        # 2 failures in 1h -> SOFT
        now = time.time()
        window = 3600
        entries = self.ledger.get_entries()
        recent_failures = [e for e in entries if e.timestamp > (now - window) and 
                           (e.decision_type == DecisionType.ACTION_ROLLBACK_FAILED or
                            (e.decision_type == DecisionType.ACTION_RESULT_RECORDED and "FAILED" in (e.reason or "")))]
        
        # Current failure + previous ones
        count = len(recent_failures) + 1 
        
        if count >= 2 and self.state.level == RecoveryLevel.NONE:
            self.escalate(RecoveryLevel.SOFT, RecoveryTrigger.FAILURE, 1800) # 30 mins

    def notify_rollback(self):
        if self.state.level != RecoveryLevel.HARD:
            self.escalate(RecoveryLevel.HARD, RecoveryTrigger.ROLLBACK, 7200) # 2 hours

    def notify_budget_exceeded(self):
        if self.state.level != RecoveryLevel.HARD:
            self.escalate(RecoveryLevel.HARD, RecoveryTrigger.BUDGET_PRESSURE, 7200)

    def escalate(self, level: RecoveryLevel, trigger: RecoveryTrigger, duration: float):
        self.state.level = level
        self.state.triggered_by = trigger
        self.state.cooldown_until = time.time() + duration
        self.state.reason = f"Triggered by {trigger.value}"
        
        print(f"[RecoveryManager] ESCALATING to {level} for {duration}s")
        self._log(DecisionType.RECOVERY_ENTERED, f"Entered {level} due to {trigger}")

    def update(self):
        # Check cooldown
        if self.state.level != RecoveryLevel.NONE:
            if time.time() > self.state.cooldown_until:
                print("[RecoveryManager] Cooldown complete. Exiting Recovery.")
                self._log(DecisionType.RECOVERY_EXITED, f"Cooldown finished for {self.state.level}")
                self.state = RecoveryState() # Reset

    def is_action_blocked(self) -> bool:
        self.update() # Check expiry first
        return self.state.level != RecoveryLevel.NONE

    def is_suggestion_blocked(self) -> bool:
        self.update()
        return self.state.level == RecoveryLevel.HARD
        
    def _log(self, dtype: DecisionType, reason: str):
        decision = AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=dtype,
            timestamp=time.time(),
            reason=reason,
            device_id=self.active_device_id
        )
        self.ledger.append(decision)
