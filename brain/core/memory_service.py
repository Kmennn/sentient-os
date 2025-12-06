from datetime import datetime, timedelta
from typing import List, Dict, Optional
import collections

class MemoryService:
    def __init__(self):
        # Structure: {user_id: collections.deque([{"role": str, "content": str, "timestamp": str}])}
        self._sessions: Dict[str, collections.deque] = {}
        self._max_history = 50
        self._ttl_minutes = 60 * 24 # 24 hours

    def _get_session(self, user_id: str) -> collections.deque:
        if user_id not in self._sessions:
            self._sessions[user_id] = collections.deque(maxlen=self._max_history)
        return self._sessions[user_id]

    def add_message(self, user_id: str, role: str, content: str):
        session = self._get_session(user_id)
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        session.append(msg)

    def get_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Returns simple list of {"role":, "content":} for LLM consumption.
        """
        session = self._get_session(user_id)
        # Convert to list and take last 'limit' items
        relevant = list(session)[-limit:]
        return [{"role": m["role"], "content": m["content"]} for m in relevant]

    def get_full_context(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Returns full context with metadata for UI/Debugging.
        """
        session = self._get_session(user_id)
        return list(session)[-limit:]

    def clear_context(self, user_id: str):
        if user_id in self._sessions:
            del self._sessions[user_id]

memory_service = MemoryService()
