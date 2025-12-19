import json
import os
import time
from typing import List, Dict, Optional
from brain.contextual.narrated_context import NarratedContext

class ContextualMemory:
    def __init__(self, persistence_path: str = "brain_data/contextual_memory_v2.jsonl"):
        self.persistence_path = persistence_path
        self._history: List[Dict] = []
        self._load()
        
    def _load(self):
        """Loads contextual memory from disk."""
        if not os.path.exists(self.persistence_path):
            return
            
        try:
            with open(self.persistence_path, "r") as f:
                for line in f:
                    if line.strip():
                        self._history.append(json.loads(line))
        except Exception as e:
            print(f"Error loading contextual memory: {e}")
            
    def add(self, narrated_context: NarratedContext, context_meta: Dict):
        """
        Adds a narrated context to memory.
        context_meta should contain: domain, risk_level, signal_type (if available)
        """
        record = narrated_context.to_dict()
        record.update(context_meta)
        record["stored_at"] = time.time()
        
        self._history.append(record)
        
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Error persisting memory: {e}")

    def get_recent(self, signal_type: str, days: int = 7) -> List[Dict]:
        """Returns entries matching signal_type within X days."""
        cutoff = time.time() - (days * 86400)
        return [
            e for e in self._history 
            if e.get("signal_id") == signal_type and e["generated_at"] > cutoff
            # Note: signal_type in user request seems to mean signal ID or Title?
            # User said "indexed by signal_type". 
            # I'll assume 'signal_title' or 'signal_id' acts as the key type.
            # Using 'title' as the grouping key is better than specific ID.
        ]

    def get_similar(self, signal_type: str, risk_level: str) -> List[Dict]:
        """Returns entries matching type and risk."""
        return [
            e for e in self._history
            if e.get("title") == signal_type and e.get("risk_level") == risk_level
            # Assuming 'title' is stored as the type identifier.
        ]

    def summarize_frequency(self, signal_type: str) -> Dict[str, int]:
        """Returns frequency counts (total, 7d, 30d)."""
        matches = [e for e in self._history if e.get("title") == signal_type]
        now = time.time()
        c7 = sum(1 for e in matches if now - e["generated_at"] < 7*86400)
        c30 = sum(1 for e in matches if now - e["generated_at"] < 30*86400)
        
        return {
            "total": len(matches),
            "7d": c7,
            "30d": c30
        }
