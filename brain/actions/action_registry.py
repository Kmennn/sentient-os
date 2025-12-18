from typing import Dict, Optional
from brain.actions.action_definition import ActionDefinition, RiskLevel

class ActionRegistry:
    def __init__(self):
        self._actions: Dict[str, ActionDefinition] = {}
        self._register_defaults()

    def _register_defaults(self):
        # 1. Maintenance Scan (Safe, Mock)
        self.register(ActionDefinition(
            id="maintenance_scan",
            name="Run Maintenance Scan",
            description="Cleans temporary memory and re-indexes internal state.",
            risk_level=RiskLevel.LOW,
            reversible=True,
            executor=self._exec_maintenance_scan
        ))

    def register(self, action: ActionDefinition):
        self._actions[action.id] = action

    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        return self._actions.get(action_id)

    def _exec_maintenance_scan(self):
        # Implementation of the safe action
        print("[ACTION] Performing Maintenance Scan...")
        # Simulate work
        import time
        time.sleep(0.1) 
        print("[ACTION] Memory Cleaned. Index Rebuilt.")
        return {"status": "success", "scanned_items": 42}
