from typing import List
import time
from brain.autonomy.autonomy_ledger import AutonomyLedger, DecisionType
from brain.timeline.cognitive_event import CognitiveEvent
from brain.timeline.timeline_narrator import TimelineNarrator

class TimelineBuilder:
    def __init__(self, ledger: AutonomyLedger):
        self.ledger = ledger
        self.narrator = TimelineNarrator()
        
    def build_timeline(self, duration_seconds: float = 86400) -> List[CognitiveEvent]:
        now = time.time()
        start_ts = now - duration_seconds
        
        # Get Entries
        # This is inefficient if ledger is huge, but v19.0 MVP
        entries = self.ledger.get_entries()
        
        events = []
        for e in entries:
            if e.timestamp < start_ts:
                continue
                
            # Map Agent
            agent = "System"
            # decision_type is Enum, access value
            dtype = e.decision_type.value if hasattr(e.decision_type, 'value') else str(e.decision_type)
            
            if "reflection" in dtype:
                agent = "Analyst"
            elif "adjustment" in dtype:
                agent = "Governor"
            elif "sync" in dtype:
                agent = "System" # Sync Layer
            elif "alert" in dtype:
                agent = "Observer" # or System filtering
                
            # Map Source
            source = "Internal"
            if e.was_auto:
                source = "Internal"
            else:
                source = "User" # Approximation
                
            # Create Event
            ce = CognitiveEvent(
                timestamp=e.timestamp,
                source=source,
                agent=agent,
                event_type=e.decision_type,
                summary=self.narrator.narrate(e),
                reference_id=e.decision_id
            )
            events.append(ce)
            
        return events
