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

import json
import os
from threading import Lock
from dataclasses import asdict
from brain.runtime.execution_state import ExecutionState, ActionPhase

class ExecutionStateStore:
    def __init__(self, storage_path: str = "brain/runtime/state.json"):
        self.storage_path = storage_path
        self._lock = Lock()
        self.state: ExecutionState = self._load()

    def _load(self) -> ExecutionState:
        if not os.path.exists(self.storage_path):
            return ExecutionState()
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                # Convert string phase to Enum
                if "action_phase" in data:
                    data["action_phase"] = ActionPhase(data["action_phase"])
                return ExecutionState(**data)
        except Exception as e:
            print(f"[ExecutionStore] Corrupt state file: {e}")
            return ExecutionState()

    def update_state(self, state: ExecutionState):
        with self._lock:
            self.state = state
            self._save()

    def update_phase(self, phase: ActionPhase, error: str = None):
        with self._lock:
            self.state.action_phase = phase
            if error:
                self.state.error = error
            self._save()
            
    def clear_state(self):
        with self._lock:
            self.state = ExecutionState()
            self._save()

    def _save(self):
        # Atomic-ish write
        temp_path = self.storage_path + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(asdict(self.state), f, default=str)
        os.replace(temp_path, self.storage_path)
    
    def get_state(self) -> ExecutionState:
        with self._lock:
            return self.state
