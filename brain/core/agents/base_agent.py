
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    """
    Abstract base class for all Sentient Agents.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def plan(self, query: str) -> List[Any]:
        """
        Analyze the query and determine steps.
        """
        pass

    @abstractmethod
    async def execute(self, step: Any) -> Any:
        """
        Execute a single step.
        """
        pass

    async def run(self, query: str) -> Any:
        """
        Default run loop: plan -> execute all steps -> return result.
        """
        plan = await self.plan(query)
        results = []
        for step in plan:
            result = await self.execute(step)
            results.append(result)
        return results
