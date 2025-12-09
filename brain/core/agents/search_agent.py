
from typing import List, Dict, Any
from .base_agent import BaseAgent
from core.vector_store import vector_store

class SearchAgent(BaseAgent):
    """
    Agent responsible for semantic search and information retrieval.
    """
    def __init__(self):
        super().__init__("SearchAgent")

    async def plan(self, query: str) -> List[str]:
        # For SearchAgent, the plan is simply the query itself 
        # (or potentially decomposed sub-queries in v2)
        return [query]

    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Searches the local vector store.
        """
        results = vector_store.search(query, k=3)
        return {
            "agent": self.name,
            "step": "vector_search",
            "query": query,
            "results": results
        }
