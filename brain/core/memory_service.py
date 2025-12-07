from datetime import datetime
from typing import List, Dict
import collections
import uuid
import time

from core.db import get_connection

class MemoryService:
    def __init__(self):
        # We keep a small LRU cache in memory to avoid hitting DB for every single token/turn
        # Structure: {user_id: collections.deque([{"role":, "content":, "timestamp":}])}
        self._cache: Dict[str, collections.deque] = {}
        self._cache_limit = 20 # Keep last 20 msgs in RAM per user

    def _get_cache(self, user_id: str) -> collections.deque:
        if user_id not in self._cache:
            self._cache[user_id] = collections.deque(maxlen=self._cache_limit)
            # Hydrate from DB on miss (optional, but good for restart)
            self._hydrate_cache(user_id)
        return self._cache[user_id]
    
    def _hydrate_cache(self, user_id: str):
        """Load recent history from DB into cache."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, text, timestamp 
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, self._cache_limit))
            rows = cursor.fetchall() # These are reversed (newest first)
            conn.close()
            
            # Re-order to chronological
            rows.reverse()
            for r in rows:
                self._cache[user_id].append({
                    "role": r[0],
                    "content": r[1],
                    "timestamp": datetime.fromtimestamp(r[2]).isoformat()
                })
        except Exception as e:
            print(f"Error hydrating cache: {e}")

    def add_message(self, user_id: str, role: str, content: str):
        ts_now = int(time.time())
        msg_id = str(uuid.uuid4())
        
        # 1. Write to DB
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (id, user_id, role, text, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (msg_id, user_id, role, content, ts_now))
            conn.commit()
            conn.close()

            # 1.5 Index in Vector Store (Fire & Forget mostly)
            from core.vector_store import vector_store
            vector_store.add(content, {
                "user_id": user_id,
                "role": role,
                "timestamp": ts_now,
                "ref_id": msg_id
            })

        except Exception as e:
            print(f"Error persisting message: {e}")

        # 2. Update Cache
        session = self._get_cache(user_id)
        msg_obj = {
            "role": role,
            "content": content,
            "timestamp": datetime.fromtimestamp(ts_now).isoformat()
        }
        session.append(msg_obj)

    def get_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Returns simple list for LLM consumption. 
        Tries cache first, falls back to DB if request exceeds cache size.
        """
        # Optimized: If limit is within cache size, return from cache
        session = self._get_cache(user_id)
        if len(session) >= limit:
            relevant = list(session)[-limit:]
            return [{"role": m["role"], "content": m["content"]} for m in relevant]
        
        # Fallback to DB query for larger context
        return self._fetch_from_db(user_id, limit)

    def _fetch_from_db(self, user_id: str, limit: int) -> List[Dict]:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, text 
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            conn.close()
            rows.reverse()
            return [{"role": r[0], "content": r[1]} for r in rows]
        except Exception as e:
            print(f"Error reading history: {e}")
            return []

    def get_full_context(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Returns full context with metadata from DB.
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, text, timestamp 
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            conn.close()
            rows.reverse()
            return [{
                "role": r[0], 
                "content": r[1], 
                "timestamp": datetime.fromtimestamp(r[2]).isoformat()
            } for r in rows]
        except Exception as e:
            print(f"Error fetching full context: {e}")
            return []

    def clear_context(self, user_id: str):
        # Clear from DB
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Soft delete or hard delete? Hard delete for 'clear' action.
            cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error clearing context: {e}")

        # Clear cache
        if user_id in self._cache:
            self._cache[user_id].clear()

memory_service = MemoryService()
