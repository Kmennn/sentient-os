
from core.tools.registry import registry
from core.tools.date_time import DateTimeTool
from core.tools.file_search import FileSearchTool
from core.tools.calculator import CalculatorTool

def register_defaults():
    registry.register(DateTimeTool())
    registry.register(FileSearchTool())
    registry.register(CalculatorTool())
