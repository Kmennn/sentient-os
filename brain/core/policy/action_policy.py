
import logging
import time
from typing import Dict, Any, Optional
from core.db import get_connection

logger = logging.getLogger("safety")

class ActionPolicy:
    def __init__(self):
        self._cache_consent = {} # user_id -> dict

    def _get_consent(self, user_id: str) -> Dict[str, bool]:
        # Simple caching
        if user_id in self._cache_consent:
            return self._cache_consent[user_id]
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT consent_actions, consent_memory, consent_vision FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                consent = {
                    "actions": bool(row[0]),
                    "memory": bool(row[1]),
                    "vision": bool(row[2])
                }
            else:
                # Default Deny if user missing
                consent = {"actions": False, "memory": False, "vision": False}
                
            self._cache_consent[user_id] = consent
            return consent
        except Exception as e:
            logger.error(f"DB Error getting consent: {e}")
            return {"actions": False, "memory": False, "vision": False}

    def check_action(self, user_id: str, action: str, details: Any) -> bool:
        """
        Check if action is allowed for user.
        Log the audit trail.
        """
        consent = self._get_consent(user_id)
        allowed = False
        reason = "Consent denied"
        
        # Policy Logic
        if action == "REAL_ACTION":
            if consent["actions"]:
                allowed = True
                reason = "User consented"
            else:
                allowed = False
                reason = "Actions consent disabled"
        elif action == "MEMORY_STORE":
            allowed = consent["memory"]
        elif action == "VISION_STORE":
            allowed = consent["vision"]
        else:
            # Default Allow for harmless internal stuff?
            # Or Default Deny?
            # Let's say safe.
            allowed = True
            reason = "Safe internal action"

        # Audit Log
        self.log_audit(user_id, action, str(details), "ALLOW" if allowed else "DENY", reason)
        return allowed

    def log_audit(self, user_id, action, resource, decision, reason):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (user_id, action, resource, decision, reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, action, resource, decision, reason, int(time.time())))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Audit log failed: {e}")

    def update_consent(self, user_id: str, updates: Dict[str, bool]):
        # Update DB
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Upsert user?
            # Check exist
            cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                fields = []
                values = []
                if "actions" in updates: 
                    fields.append("consent_actions = ?")
                    values.append(updates["actions"])
                if "memory" in updates:
                    fields.append("consent_memory = ?")
                    values.append(updates["memory"])
                if "vision" in updates:
                    fields.append("consent_vision = ?")
                    values.append(updates["vision"])
                
                if fields:
                    values.append(user_id)
                    cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", values)
            else:
                # Create default + updates
                c_act = updates.get("actions", False)
                c_mem = updates.get("memory", False)
                c_vis = updates.get("vision", False)
                cursor.execute("""
                    INSERT INTO users (user_id, username, consent_actions, consent_memory, consent_vision, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, "default_user", c_act, c_mem, c_vis, int(time.time())))
                
            conn.commit()
            conn.close()
            # Invalidate cache
            if user_id in self._cache_consent:
                del self._cache_consent[user_id]
        except Exception as e:
            logger.error(f"Consent update failed: {e}")
            raise e

action_policy = ActionPolicy()
