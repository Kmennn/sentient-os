import time
import uuid
from typing import Dict, Optional
from brain.actions.action_capability import ActionCapability, ActionRisk
from brain.autonomy.autonomy_ledger import AutonomyLedger, AutonomyDecision, DecisionType

class ActionSandbox:
    def __init__(self, ledger: AutonomyLedger, scheduler):
        self.ledger = ledger
        self.scheduler = scheduler
        self._capabilities: Dict[str, ActionCapability] = {}
        self._register_defaults()

    def _register_defaults(self):
        # Demo Capability
        self.register_capability(ActionCapability(
            action_id="demo_safe_ping",
            description="Emits a ping log. Completely safe.",
            risk_level=ActionRisk.LOW,
            reversible=True,
            requires_consent=False
        ))
        
        self.register_capability(ActionCapability(
            action_id="demo_risky_reset",
            description="Resets internal counters. Risky.",
            risk_level=ActionRisk.HIGH,
            reversible=False,
            requires_consent=True
        ))

    def register_capability(self, cap: ActionCapability):
        self._capabilities[cap.action_id] = cap

    def execute_action(self, action_id: str, requesting_agent: str = "User") -> bool:
        cap = self._capabilities.get(action_id)
        if not cap:
            self._log(DecisionType.ACTION_BLOCKED, action_id, "Unknown Action ID")
            return False

        # Safety Check via Scheduler context
        if not self.scheduler.is_safe_to_execute(cap):
            self._log(DecisionType.ACTION_BLOCKED, action_id, "Safety Checks Failed (Trust/Confidence/Focus)")
            return False

        # Execution (Sandbox simulation)
        try:
            # Enforce Timeout (Simulator)
            start = time.time()
            if action_id == "demo_safe_ping":
                 print(f"[SANDBOX] PING! Executed by {requesting_agent}")
            elif action_id == "demo_risky_reset":
                 print(f"[SANDBOX] RESET! Executed by {requesting_agent}")
            
            # Simulated processing time check
            if time.time() - start > 1.0:
                 raise TimeoutError("Action exceeded 1s execution limit")
            
            self._log(DecisionType.ACTION_EXECUTED, action_id, "Success")
            return True

        except Exception as e:
            self._log(DecisionType.ACTION_BLOCKED, action_id, f"Runtime Error: {e}")
            return False

    def revert_action(self, action_id: str) -> bool:
        cap = self._capabilities.get(action_id)
        if not cap or not cap.reversible:
            self._log(DecisionType.ACTION_BLOCKED, action_id, "Cannot revert irreversible or unknown action")
            return False
            
        print(f"[SANDBOX] REVERTING {action_id}")
        self._log(DecisionType.ACTION_REVERTED, action_id, "Reverted successfully")
        return True

    def _log(self, dtype: DecisionType, action_id: str, reason: str):
        decision = AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=dtype,
            timestamp=time.time(),
            action_id=action_id,
            reason=reason,
            device_id=self.scheduler.active_device_id
        )
        self.ledger.append(decision)
