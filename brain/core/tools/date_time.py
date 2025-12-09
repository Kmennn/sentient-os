
from core.tools.registry import BaseTool
from datetime import datetime
from typing import Dict, Any

class DateTimeTool(BaseTool):
    name = "date_time"
    description = "Returns the current date and time."

    def run(self, params: Dict[str, Any]) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
