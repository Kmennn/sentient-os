import logging
import json
import os
import time
from typing import Optional, List
from brain.context.signals.context_signal_model import ContextSignal, ContextSource

class CalendarProvider:
    """
    Read-only provider for calendar events.
    Currently reads from a 'calendar_cache.json' in user home or configured path.
    """
    def __init__(self, cache_path: str = None):
        self.logger = logging.getLogger(__name__)
        # Default to a safe location
        self.cache_path = cache_path or os.path.expanduser("~/.sentient/calendar_cache.json")

    def check_status(self) -> Optional[ContextSignal]:
        """
        Returns a signal if there is an active or upcoming meeting within threshold.
        """
        events = self._load_events()
        if not events:
            return None
            
        now = time.time()
        current_meeting = None
        upcoming_meeting = None
        
        for event in events:
            start = event.get("start_timestamp", 0)
            end = event.get("end_timestamp", 0)
            
            # Active
            if start <= now <= end:
                current_meeting = event
                break # Priority
            
            # Upcoming (within 15m)
            if now < start <= now + 900:
                if not upcoming_meeting or start < upcoming_meeting["start_timestamp"]:
                    upcoming_meeting = event
        
        data = {}
        if current_meeting:
            data["status"] = "in_meeting"
            data["event"] = current_meeting
        elif upcoming_meeting:
            data["status"] = "meeting_soon"
            data["event"] = upcoming_meeting
        else:
            return None # No signal needed if free
            
        return ContextSignal(
            source=ContextSource.CALENDAR,
            data=data
        )

    def _load_events(self) -> List[dict]:
        if not os.path.exists(self.cache_path):
            return []
        try:
            with open(self.cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load calendar cache: {e}")
            return []
