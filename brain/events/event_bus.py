import logging
import asyncio
from typing import Callable, Dict, List, Any
from brain.events.event_types import EventType

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._async_subscribers: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        
    def subscribe_async(self, event_type: EventType, handler: Callable):
        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []
        self._async_subscribers[event_type].append(handler)

    def emit(self, event_type: EventType, data: Any = None):
        # Synchronous handlers
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in sync/event handler for {event_type}: {e}")
                    
        # Async handlers (fire and forget task)
        if event_type in self._async_subscribers:
             for handler in self._async_subscribers[event_type]:
                 try:
                     asyncio.create_task(handler(data))
                 except Exception as e:
                     # This might fail if no loop is running, expected in some sync contexts
                     logger.warning(f"Could not dispatch async event {event_type} (No Loop?): {e}")

event_bus = EventBus()
