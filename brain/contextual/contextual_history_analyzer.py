import time
from typing import List, Dict, Tuple
from brain.contextual.contextual_memory_store import ContextualMemoryStore

class ContextualHistoryAnalyzer:
    def __init__(self, memory_store: ContextualMemoryStore):
        self.memory_store = memory_store
        
    def analyze_history(self, signal_domain: str, signal_title: str) -> Tuple[int, int, str]:
        """
        Analyzes history for similar signals.
        Returns: (count_7d, count_30d, trend_label)
        Matching based on domain comparison (simplified for now).
        """
        history = self.memory_store.get_history()
        now = time.time()
        
        # Simplified similarity: Same 'domain' (stored in context dict?)
        # NarratedContext dict doesn't have domain explicitly, but we can assume caller passes it 
        # or we check 'summary_text' or 'signal_id' patterns.
        # Actually, let's use signal_title keywords or just naive signal_id matching if stable?
        # Signal IDs are GUIDs, so they won't match across events.
        # Let's perform fuzzy match on SUMMARY or TITLE if provided.
        # For v14.0, we will assume we store 'title' in the memory record (from context).
        # Need to ensure we record 'title' or 'domain' when saving.
        
        # Filter matching events
        matches = []
        for entry in history:
            # Check similarity. We'll use a simple keyword check from the new title provided.
            # Assuming entry has 'summary_text'.
            # A better way is if we update the storage to include 'title' or 'domain'.
            # I'll update the caller (Scheduler) to include 'title' in the dict it saves.
            
            if "title" in entry and entry["title"] == signal_title:
                matches.append(entry)
            elif "summary_text" in entry and signal_title.lower() in entry["summary_text"].lower():
                 matches.append(entry)
                 
        # Counts
        count_7d = 0
        count_30d = 0
        
        for m in matches:
            age = now - m["generated_at"]
            if age < 7 * 86400:
                count_7d += 1
            if age < 30 * 86400:
                count_30d += 1
                
        # Trend
        trend = "new"
        if len(matches) > 1:
            if count_7d > (count_30d / 4) * 1.5: # Naive: if recent week is > 1.5x average week
                trend = "increasing"
            elif count_7d == 0:
                trend = "stable"
            else:
                trend = "stable"
        elif len(matches) == 1:
            trend = "new" # First recurrence (since we just added current?) 
            # Actually this function is called BEFORE saving current? 
            # User requirement: "Given a new signal... answer".
            # So if matches > 0, it's "recurrence".
            trend = "recurring"
            
        return count_7d, count_30d, trend
