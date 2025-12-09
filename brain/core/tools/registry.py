
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger("tools")

class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Abstract base tool"

    @abstractmethod
    def run(self, params: Dict[str, Any]) -> Any:
        pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        if tool.name in self._tools:
            logger.warning(f"Overwriting tool: {tool.name}")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

# Global Registry
registry = ToolRegistry()
