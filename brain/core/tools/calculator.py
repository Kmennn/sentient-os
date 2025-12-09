from typing import Dict, Any
from core.tools.registry import BaseTool

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluates a mathematical expression (e.g., '2 + 2')."
    
    def run(self, params: Dict[str, Any]) -> Any:
        expression = params.get("expression", "")
        if not expression:
            return "Error: No expression provided."
        
        # Security: Simple eval is dangerous. We should use a safer parser.
        # MVP: Restrict characters.
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters in expression."
        
        try:
            # Evaluate using safest simple eval
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {e}"
