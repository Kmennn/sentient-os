from datetime import datetime
from typing import List, Dict, Any
import collections

class EventLog:
    def __init__(self):
        self._events = collections.deque(maxlen=100)
    
    def log_event(self, type: str, payload: Any):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": type,
            "payload": payload
        }
        self._events.append(event)
        print(f"[EVENT] [{type}] {payload}")
        
        # v1.5 Persistence Stub (Append to file)
        try:
            with open("events.log", "a") as f:
                import json
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Log error: {e}")

    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        return list(self._events)[-limit:]

event_log = EventLog()
