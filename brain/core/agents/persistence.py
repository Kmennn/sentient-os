
import json
import logging
import time
from typing import Dict, Any, Optional
from core.db import get_connection

logger = logging.getLogger("persistence")

class AgentPersistence:
    def log_step(self, agent_name: str, step_name: str, details: Dict[str, Any]):
        """
        Log an agent execution step to the DB.
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_logs (agent_name, step, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (agent_name, step_name, json.dumps(details), int(time.time())))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log step: {e}")

    def get_logs(self, agent_name: str, limit: int = 10):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT step, details, timestamp FROM agent_logs
                WHERE agent_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_name, limit))
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "step": r[0],
                    "details": json.loads(r[1]) if r[1] else {},
                    "timestamp": r[2]
                }
                for r in rows
            ]
        except Exception as e:
            logger.error(f"Failed to fetch logs: {e}")
            return []

persistence_service = AgentPersistence()
