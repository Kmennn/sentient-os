# ==========================================
# ⚠️ STABILITY ZONE — FEATURE FROZEN
#
# This file is part of Sentient OS core logic.
# Feature-frozen as of v22.0.0.
#
# Allowed:
# - Bug fixes
# - Refactors without behavior change
#
# Forbidden:
# - New features
# - New decision logic
# - New autonomy paths
#
# All changes must preserve behavior.
# ==========================================

import time
import uuid
from typing import Dict, Optional
from brain.actions.action_capability import ActionCapability, ActionRisk
from brain.actions.action_result import ActionResult, ActionStatus
from brain.actions.action_rollback import ActionRollback
from brain.autonomy.autonomy_ledger import AutonomyLedger, AutonomyDecision, DecisionType
from brain.runtime.execution_state import ExecutionState, ActionPhase

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

        self.register_capability(ActionCapability(
            action_id="native_exec",
            description="Executes a real system command (Whitelisted).",
            risk_level=ActionRisk.HIGH,
            reversible=False,
            requires_consent=True # Always require consent for real ops
        ))

    def register_capability(self, cap: ActionCapability):
        self._capabilities[cap.action_id] = cap



    def execute_action(self, action_id: str, requesting_agent: str = "User") -> ActionResult:
        cap = self._capabilities.get(action_id)
        if not cap:
            self._log(DecisionType.ACTION_BLOCKED, action_id, "Unknown Action ID")
            return ActionResult(action_id, ActionStatus.FAILED, False, error_reason="Unknown ID")

        # Safety Check via Scheduler
        if not self.scheduler.is_safe_to_execute(cap):
            self._log(DecisionType.ACTION_BLOCKED, action_id, "Safety Checks Failed")
            return ActionResult(action_id, ActionStatus.FAILED, cap.reversible, error_reason="Safety Blocked")

        # PERSISTENCE (v22.0)
        store = getattr(self.scheduler, 'execution_store', None)
        if store:
            state = ExecutionState(
                active_action_id=action_id,
                action_phase=ActionPhase.EXECUTING,
                started_at=time.time(),
                context_snapshot={"trust": self.scheduler.device_trust_score}
            )
            store.update_state(state)

        # Execution
        try:
            # Enforce Timeout (Simulator)
            start = time.time()
            if action_id == "demo_safe_ping":
                 print(f"[SANDBOX] PING! Executed by {requesting_agent}")
            elif action_id == "demo_risky_reset":
                 print(f"[SANDBOX] RESET! Executed by {requesting_agent}")
            elif action_id == "native_exec":
                cmd = self._capabilities[action_id].params.get("command", "")
                # Real Sandbox: Whitelist
                allowed = ["notepad.exe", "calc.exe", "echo"]
                if not any(cmd.startswith(a) for a in allowed) and not cmd.startswith("echo"):
                     raise ValueError(f"Command '{cmd}' not in safety whitelist: {allowed}")
                
                import subprocess
                # Run detached
                subprocess.Popen(cmd, shell=True)
                print(f"[SANDBOX] Launching Real Process: {cmd}")

            # Simulated processing
            if time.time() - start > 1.0:
                 raise TimeoutError("Action exceeded 1s execution limit")
            
            self._log(DecisionType.ACTION_EXECUTED, action_id, "Success")
            self._log(DecisionType.ACTION_RESULT_RECORDED, action_id, "Result: SUCCESS")
            
            self.scheduler.record_action_outcome(action_id, ActionStatus.SUCCESS)
            
            # PERSISTENCE: Success
            if store:
                store.update_phase(ActionPhase.COMPLETED)

            return ActionResult(action_id, ActionStatus.SUCCESS, cap.reversible)

        except Exception as e:
            self._log(DecisionType.ACTION_BLOCKED, action_id, f"Runtime Error: {e}")
            self.scheduler.record_action_outcome(action_id, ActionStatus.FAILED)
            
            # PERSISTENCE: Failure (Handled Error)
            if store:
                store.update_phase(ActionPhase.FAILED, error=str(e))
                
            return ActionResult(action_id, ActionStatus.FAILED, cap.reversible, error_reason=str(e))
            
    def revert_action(self, action_id: str) -> bool:
        return ActionRollback.execute_rollback(action_id, self)

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
