from typing import Set, Dict

class ActionPolicy:
    def __init__(self):
        # Default policy: Deny all real actions unless explicitly allowed
        self._allowlist: Dict[str, Set[str]] = {} # user_id -> set of allowed intents
        self._denylist: Set[str] = {"shutdown", "format_drive", "delete_system32"} # Global dangerous actions

    def allow_intent(self, user_id: str, intent: str) -> bool:
        """
        Check if an intent is allowed for the given user.
        """
        if intent in self._denylist:
            return False
            
        # In v1.5, we require explicit per-action confirmation for everything
        # unless it's in the allowlist. 
        # But for now, the flow is:
        # 1. Check if allowed -> If yes, Execute immediately (Autonomy Level 2)
        # 2. If not allowed -> Request Confirmation -> If confirmed -> Execute (Autonomy Level 1)
        
        # For this sprint, we just return False here to force Confirmation every time
        # unless user has explicitly "remembered" it.
        
        user_allows = self._allowlist.get(user_id, set())
        return intent in user_allows

    def grant(self, user_id: str, intent: str):
        if user_id not in self._allowlist:
            self._allowlist[user_id] = set()
        self._allowlist[user_id].add(intent)
        print(f"[POLICY] Granted '{intent}' to {user_id}")

    def revoke(self, user_id: str, intent: str):
        if user_id in self._allowlist and intent in self._allowlist[user_id]:
            self._allowlist[user_id].remove(intent)
            print(f"[POLICY] Revoked '{intent}' from {user_id}")

action_policy = ActionPolicy()
