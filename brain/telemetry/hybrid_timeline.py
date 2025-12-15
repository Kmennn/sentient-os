
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HybridTimeline:
    """
    Chronological record of hybrid decision events.
    Used for telemetry and debugging.
    """
    def __init__(self):
        self._events: List[Dict[str, Any]] = []
        
    def add_event(self, event_type: str, message: str, metadata: Dict[str, Any] = None):
        """
        Types: PLAN, POLICY, ALPHA_CHANGE, FALLBACK, SUPERVISOR
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "metadata": metadata or {}
        }
        self._events.append(entry)
        # log to disk/logger too
        logger.info(f"TIMELINE [{event_type}]: {message}")
        
    def get_events(self, limit: int = 100) -> List[Dict]:
        return self._events[-limit:]

hybrid_timeline = HybridTimeline()
