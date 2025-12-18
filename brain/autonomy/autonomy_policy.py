import json
import os
from typing import Dict, Any, Tuple
from dataclasses import dataclass, field

from brain.actions.action_definition import RiskLevel
from brain.preferences.interrupt_style import InterruptStyle

@dataclass
class ActionStats:
    success_count: int = 0
    dismissal_count: int = 0
    last_executed: float = 0.0

class AutonomyPolicy:
    def __init__(self, persistence_path="brain/autonomy/autonomy_stats.json"):
        self.persistence_path = persistence_path
        self._stats: Dict[str, ActionStats] = {}
        self.enabled = True # Kill-switch
        self._load()

    def may_auto_execute(self, action_id: str, action_def: Any, 
                         trust_score: float, 
                         interrupt_style: InterruptStyle, 
                         focus_active: bool, 
                         presence_public: bool) -> Tuple[bool, str]:
        
        # 0. Global Switch
        if not self.enabled:
            return False, "Autonomy Disabled"

        # 1. Trust
        if trust_score < 0.95:
            return False, f"Trust too low ({trust_score:.2f} < 0.95)"

        # 2. Interrupt Style
        if interrupt_style == InterruptStyle.NEVER_INTERRUPT:
             # Even for auto-execute, we prefer NOT to act if user wants absolute silence?
             # Or does "NEVER INTERRUPT" mean "Don't ask me"? 
             # Requirement says: "User Interrupt Style != never_interrupt"
             return False, "User requested No Interrupts"

        # 3. Focus
        if focus_active:
            return False, "Focus Active"

        # 4. Presence
        if presence_public:
            return False, "Presence is Public"

        # 5. Risk
        if action_def.risk_level != RiskLevel.LOW:
            return False, "Risk too high"

        # 6. History
        stats = self._get_stats(action_id)
        if stats.dismissal_count > 0:
            return False, "Action previously dismissed"
        
        if stats.success_count < 5:
            return False, f"Insufficient success history ({stats.success_count}/5)"

        return True, "Approved"

    def record_success(self, action_id: str):
        stats = self._get_stats(action_id)
        stats.success_count += 1
        import time
        stats.last_executed = time.time()
        self._save()

    def record_dismissal(self, action_id: str):
        stats = self._get_stats(action_id)
        stats.dismissal_count += 1
        self._save()

    def disable_autonomy(self, reason: str):
        self.enabled = False
        print(f"[AUTONOMY] KILL-SWITCH ENGAGED: {reason}")
        # Could persist this state too

    def _get_stats(self, action_id: str) -> ActionStats:
        if action_id not in self._stats:
            self._stats[action_id] = ActionStats()
        return self._stats[action_id]

    def _load(self):
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, 'r') as f:
                    data = json.load(f)
                    for aid, s in data.items():
                        self._stats[aid] = ActionStats(
                            success_count=s.get('success_count', 0),
                            dismissal_count=s.get('dismissal_count', 0),
                            last_executed=s.get('last_executed', 0.0)
                        )
            except Exception as e:
                print(f"Failed to load user stats: {e}")

    def _save(self):
        try:
            data = {}
            for aid, s in self._stats.items():
                data[aid] = {
                    'success_count': s.success_count,
                    'dismissal_count': s.dismissal_count,
                    'last_executed': s.last_executed
                }
            # Ensure dir
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save user stats: {e}")
