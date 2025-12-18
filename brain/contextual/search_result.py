from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class SearchResult:
    query: str
    summary: str
    sources: List[str]
    confidence_score: float
    signal_id: str
    fetched_at: float = 0.0
    
    def __post_init__(self):
        if self.fetched_at == 0.0:
            self.fetched_at = time.time()
            
    def to_dict(self):
        return {
            "query": self.query,
            "summary": self.summary,
            "sources": self.sources,
            "confidence_score": self.confidence_score,
            "signal_id": self.signal_id,
            "fetched_at": self.fetched_at
        }
