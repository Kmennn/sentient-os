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
from typing import Optional, List
from brain.autonomy.override_token import OverrideToken, OverrideScope
from brain.autonomy.autonomy_ledger import AutonomyLedger, AutonomyDecision, DecisionType

class OverrideManager:
    def __init__(self, ledger: AutonomyLedger):
        self.ledger = ledger
        self.active_token: Optional[OverrideToken] = None
        self.active_device_id = "unknown"

    def update_device_id(self, device_id: str):
        self.active_device_id = device_id

    def request_override(self, scope: OverrideScope, reason: str, requested_by: str = "User") -> OverrideToken:
        token = OverrideToken(
            override_id=str(uuid.uuid4()),
            requested_by=requested_by,
            reason=reason,
            scope=scope,
            issued_at=time.time(),
            expires_at=time.time() + 600 # 10 Minutes
        )
        self.active_token = token
        
        self._log(DecisionType.OVERRIDE_REQUESTED, f"Requested {scope} override: {reason}")
        self._log(DecisionType.OVERRIDE_GRANTED, f"Granted {token.override_id}")
        
        return token

    def get_active_token(self) -> Optional[OverrideToken]:
        if self.active_token:
            if self.active_token.is_valid():
                return self.active_token
            else:
                if not self.active_token.used: # Log expiry once
                     self._log(DecisionType.OVERRIDE_EXPIRED, f"Token {self.active_token.override_id} expired")
                self.active_token = None
        return None

    def has_override(self, scope: OverrideScope) -> bool:
        token = self.get_active_token()
        if not token:
            return False
        if token.scope == OverrideScope.ALL or token.scope == scope:
            return True
        return False
        
    def use_override(self, scope: OverrideScope, context: str):
        token = self.get_active_token()
        if token and (token.scope == OverrideScope.ALL or token.scope == scope):
             self._log(DecisionType.OVERRIDE_USED, f"Used override for {context}")
             # We keep it active for the duration (time-bound) rather than one-time consumption
             # unless needed.

    def _log(self, dtype: DecisionType, reason: str):
        decision = AutonomyDecision(
            decision_id=str(uuid.uuid4()),
            decision_type=dtype,
            timestamp=time.time(),
            reason=reason,
            device_id=self.active_device_id
        )
        self.ledger.append(decision)
