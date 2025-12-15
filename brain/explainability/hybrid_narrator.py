
import logging
from typing import List, Dict
from brain.telemetry.hybrid_timeline import HybridTimeline, hybrid_timeline

logger = logging.getLogger(__name__)

class HybridNarrator:
    """
    Constructs a human-readable narrative of the hybrid execution process.
    """
    def __init__(self, timeline: HybridTimeline = hybrid_timeline):
        self.timeline = timeline
        
    def generate_narrative(self) -> str:
        """
        Summarizes recent timeline events.
        """
        events = self.timeline.get_events(limit=10) # Last 10 relevant
        if not events:
            return "No recent activity."
            
        narrative = []
        for e in events:
            t_iso = e['timestamp'].split('T')[1][:8] # HH:MM:SS
            msg = e['message']
            
            if e['type'] == "ALPHA_CHANGE":
                narrative.append(f"[{t_iso}] Control shifted: {msg}")
            elif e['type'] == "FALLBACK":
                 narrative.append(f"[{t_iso}] SAFETY FALLBACK: {msg}")
            elif e['type'] == "POLICY":
                 narrative.append(f"[{t_iso}] Policy suggested: {msg}")
            else:
                 narrative.append(f"[{t_iso}] {msg}")
                 
        return "\n".join(narrative)

hybrid_narrator = HybridNarrator()
