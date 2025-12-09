
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
        self.autodiscover()

    def register(self, tool: BaseTool):
        if tool.name in self._tools:
            logger.warning(f"Overwriting tool: {tool.name}")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def autodiscover(self):
        """
        Dynamically find and register tools in core.tools package.
        """
        import pkgutil
        import importlib
        import inspect
        import core.tools
        
        package = core.tools
        prefix = package.__name__ + "."
        
        for _, name, _ in pkgutil.iter_modules(package.__path__, prefix):
            try:
                module = importlib.import_module(name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (inspect.isclass(attr) and 
                        issubclass(attr, BaseTool) and 
                        attr is not BaseTool and
                        attr.__module__ == module.__name__): # Ensure it's defined here
                        
                        tool_instance = attr()
                        self.register(tool_instance)
            except Exception as e:
                logger.error(f"Failed to auto-register tool from {name}: {e}")

# Global Registry
registry = ToolRegistry()

